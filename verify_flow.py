"""End-to-end check of the screenshot-verification and slot/vehicle flows."""
import base64
import json
import os
import sys
import io
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'testing'

from backend.app import create_app
from backend.models import db, User, Notification, Booking, Payment, BookingVehicle, Facility, Slot
from backend.utils.helpers import utcnow

app = create_app('testing')
client = app.test_client()

PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)

fails = []


def check(label, cond, extra=''):
    print(('  PASS  ' if cond else '  FAIL  ') + label + (f'   {extra}' if extra else ''))
    if not cond:
        fails.append(label)


def login(email, password):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    body = res.get_json()
    assert res.status_code == 200, body
    return {'Authorization': 'Bearer ' + body['access_token']}


def png_base64():
    return 'data:image/png;base64,' + base64.b64encode(PNG).decode()


with app.app_context():
    db.drop_all()
    db.create_all()

    from werkzeug.security import generate_password_hash
    admin = User(user_id='PKR-A-1', full_name='Admin One', email='admin@test.com', phone='9000000001',
                 password_hash=generate_password_hash('Admin@123'), role='admin')
    user = User(user_id='PKR-U-1', full_name='Ravi Kumar', email='ravi@test.com', phone='9000000002',
                password_hash=generate_password_hash('User@123'), role='user')
    fac = Facility(facility_id='FAC-T-1', name='Test Park', street='Street 1', area='Area', city='Pune',
                   pincode='411001', latitude=18.5, longitude=73.9,
                   total_car=3, available_car=3, rate_car_hourly=40, monthly_car=8000)
    db.session.add_all([admin, user, fac])
    db.session.flush()
    for i in range(1, 4):
        db.session.add(Slot(facility_id=fac.id, slot_code=f'C{i}', vehicle_type='Car'))
    db.session.commit()
    facility_id = fac.id

admin_h = login('admin@test.com', 'Admin@123')
user_h = login('ravi@test.com', 'User@123')

start = (utcnow() + timedelta(hours=2)).replace(microsecond=0)
end = start + timedelta(hours=2)


def make_booking(slots, vehicles, use_legacy=False):
    payload = {
        'facility_id': facility_id,
        'vehicle_type': 'Car',
        'start_time': start.isoformat() + 'Z',
        'end_time': end.isoformat() + 'Z',
        'duration_value': 2,
        'duration_unit': 'hours',
        'slot_codes': slots,
    }
    if use_legacy:
        payload['vehicle_no'] = vehicles[0]
    else:
        payload['vehicle_nos'] = vehicles
    return client.post('/api/bookings', json=payload, headers=user_h)


print('\n=== 1. One vehicle number per slot ===')

res = make_booking(['C1', 'C2'], ['MH12AB1234'])
check('2 slots with only 1 vehicle number is rejected', res.status_code == 400,
      res.get_json().get('error', ''))

res = make_booking(['C1', 'C2'], ['MH12AB1234', 'MH12AB1234'])
check('duplicate vehicle numbers are rejected', res.status_code == 400,
      res.get_json().get('error', ''))

res = make_booking(['C1', 'C2'], ['MH12AB1234', ''])
check('blank vehicle number is rejected', res.status_code == 400,
      res.get_json().get('error', ''))

res = make_booking(['C1'], [])
check('no vehicle numbers at all is rejected', res.status_code == 400,
      res.get_json().get('error', ''))

res = make_booking(['C1', 'C2'], ['MH12AB1234', 'MH12AB1235'])
check('2 slots + 2 vehicle numbers is accepted', res.status_code == 201, res.get_json().get('error', ''))
booking2 = res.get_json()['booking']
check('vehicles persisted per slot', booking2.get('vehicles') == ['MH12AB1234', 'MH12AB1235'],
      str(booking2.get('vehicles')))
check('booking_vehicles rows written', len(booking2.get('vehicles') or []) == 2)
check('vehicle numbers upper-cased', make_booking(['C3'], ['mh12zz9999']).get_json()['booking']['vehicles'] == ['MH12ZZ9999'])

with app.app_context():
    check('BookingVehicle rows exist in DB',
          BookingVehicle.query.filter_by(booking_id=booking2['id']).count() == 2)
    # free C1/C2/C3 for the next steps
    for code in ('C1', 'C2', 'C3'):
        s = Slot.query.filter_by(facility_id=facility_id, slot_code=code).first()
        s.is_occupied = False
        s.occupied_until = None
    db.session.commit()

print('\n=== 2. Price scales with slot count ===')
with app.app_context():
    from backend.utils.helpers import calculate_price
    fac = Facility.query.get(facility_id)
    one = calculate_price(fac, 'Car', 2, 'hours', start, slot_count=1)['total_amount']
    two = calculate_price(fac, 'Car', 2, 'hours', start, slot_count=2)['total_amount']
    check('2 slots cost exactly 2x 1 slot', abs(two - one * 2) < 0.01, f'{one} vs {two}')

print('\n=== 3. Screenshot upload notifies admins ===')
res = client.post('/api/bookings', json={
    'facility_id': facility_id, 'vehicle_nos': ['MH01AA0001'], 'vehicle_type': 'Car',
    'start_time': start.isoformat() + 'Z', 'end_time': end.isoformat() + 'Z',
    'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}, headers=user_h)
booking = APIbooking = res.get_json()['booking']

res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': booking['id'], 'screenshot_base64': png_base64(),
                        'transaction_id': 'UPI123456789'},
                  headers=user_h)
check('screenshot upload accepted', res.status_code == 200, res.get_json().get('error', ''))
payment = res.get_json()['payment']
check('payment status is pending_screenshot', payment['status'] == 'pending_screenshot')
check('booking flagged pending_verification',
      res.get_json()['booking']['payment_status'] == 'pending_verification')

with app.app_context():
    admin_user = User.query.filter_by(email='admin@test.com').first()
    notes = Notification.query.filter_by(user_id=admin_user.id).all()
    check('admin got a notification', len(notes) == 1, str([n.title for n in notes]))
    check('notification type is payment_verification',
          bool(notes) and notes[0].ntype == 'payment_verification')
    check('notification links to admin view', bool(notes) and notes[0].link == 'admin')

res = client.get('/api/notifications', headers=admin_h)
check('admin notification is listed', res.status_code == 200 and
      len(res.get_json()['notifications']) == 1)
check('admin unread count is 1', res.get_json()['unread_count'] == 1)

print('\n=== 4. Admin verification queue ===')
res = client.get('/api/admin/payments/pending', headers=admin_h)
check('queue endpoint lists the payment', res.status_code == 200 and
      res.get_json()['pending_count'] == 1, res.get_json())
item = res.get_json()['verifications'][0]
check('queue item exposes the screenshot url', bool(item.get('screenshot_url')),
      str(item.get('screenshot_url')))
check('queue item includes user + booking', bool(item.get('user')) and bool(item.get('booking')))

res = client.get('/api/admin/payments/pending', headers=user_h)
check('normal user cannot read the queue', res.status_code == 403)

res = client.post(f"/api/payments/admin/verify-screenshot/{payment['id']}",
                  json={'action': 'approve'}, headers=user_h)
check('normal user cannot approve', res.status_code == 403)

print('\n=== 5. Screenshot file access control ===')
# A brand-new client: the shared `client` still holds auth cookies from login.
anon = app.test_client()
res = anon.get(item['screenshot_url'])
check('screenshot requires auth (no token)', res.status_code == 401, str(res.status_code))
res = client.get(item['screenshot_url'], headers=user_h)
check('owner can view own screenshot', res.status_code == 200, str(res.status_code))
res = client.get(item['screenshot_url'], headers=admin_h)
check('admin can view screenshot', res.status_code == 200)

with app.app_context():
    other = User(user_id='PKR-U-2', full_name='Other User', email='other@test.com', phone='9000000003',
                 password_hash=generate_password_hash('User@123'), role='user')
    db.session.add(other)
    db.session.commit()
other_h = login('other@test.com', 'User@123')
res = client.get(item['screenshot_url'], headers=other_h)
check("another user cannot view someone else's screenshot", res.status_code == 403, str(res.status_code))

print('\n=== 6. Admin approves payment ===')
res = client.post(f"/api/payments/admin/verify-screenshot/{payment['id']}",
                  json={'action': 'approve', 'notes': 'Matches bank statement'},
                  headers=admin_h)
check('approve succeeds', res.status_code == 200, res.get_json().get('error', ''))
body = res.get_json()
check('booking is paid + confirmed',
      body['booking']['payment_status'] == 'paid' and body['booking']['status'] == 'confirmed')
check('transaction id recorded', body['booking']['transaction_id'] == 'UPI123456789',
      str(body['booking']['transaction_id']))
gw = json.loads(body['payment']['gateway_response'])
check('real admin recorded as verifier', gw.get('verified_by') == admin_user.user_id, str(gw.get('verified_by')))
check('approval note stored', gw.get('notes') == 'Matches bank statement')
check('no absolute path leaked', 'screenshot_path' not in gw, str(gw))

res = client.post(f"/api/payments/admin/verify-screenshot/{payment['id']}",
                  json={'action': 'approve'}, headers=admin_h)
check('double approval is blocked', res.status_code == 409, str(res.status_code))

with app.app_context():
    user_row = User.query.filter_by(email='ravi@test.com').first()
    user_notes = Notification.query.filter_by(user_id=user_row.id).all()
    check('user got approval notification', len(user_notes) == 1,
          str([(n.ntype, n.title) for n in user_notes]))
    check('approval notification type', bool(user_notes) and user_notes[0].ntype == 'payment_approved')

print('\n=== 7. Admin rejects payment and slots are released ===')
res = client.post('/api/bookings', json={
    'facility_id': facility_id, 'vehicle_nos': ['MH02BB0002'], 'vehicle_type': 'Car',
    'start_time': start.isoformat() + 'Z', 'end_time': end.isoformat() + 'Z',
    'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C2']}, headers=user_h)
b2 = res.get_json()['booking']

with app.app_context():
    s = Slot.query.filter_by(facility_id=facility_id, slot_code='C2').first()
    check('slot held before payment', s.is_occupied)

res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': b2['id'], 'screenshot_base64': png_base64()},
                  headers=user_h)
p2 = res.get_json()['payment']
res = client.post(f"/api/payments/admin/verify-screenshot/{p2['id']}",
                  json={'action': 'reject', 'notes': 'Amount mismatch'}, headers=admin_h)
check('reject succeeds', res.status_code == 200, res.get_json().get('error', ''))
body = res.get_json()
check('booking marked failed + cancelled',
      body['booking']['payment_status'] == 'failed' and body['booking']['status'] == 'cancelled')

with app.app_context():
    s = Slot.query.filter_by(facility_id=facility_id, slot_code='C2').first()
    check('slot released back to pool after reject', not s.is_occupied)
    user_row = User.query.filter_by(email='ravi@test.com').first()
    kinds = [n.ntype for n in Notification.query.filter_by(user_id=user_row.id).order_by(Notification.id)]
    check('user got rejection notification', 'payment_rejected' in kinds, str(kinds))
    last = Notification.query.filter_by(user_id=user_row.id, ntype='payment_rejected').first()
    check('rejection note included in notification',
          last is not None and 'Amount mismatch' in (last.message or ''), str(last and last.message))

print('\n=== 8. Upload validation ===')
# Use a fresh, still-live booking so the image checks are what actually rejects.
res = client.post('/api/bookings', json={
    'facility_id': facility_id, 'vehicle_nos': ['MH04DD0004'], 'vehicle_type': 'Car',
    'start_time': start.isoformat() + 'Z', 'end_time': end.isoformat() + 'Z',
    'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C3']}, headers=user_h)
b3 = res.get_json()['booking']

res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': b3['id'], 'screenshot_base64': base64.b64encode(b'not an image').decode()},
                  headers=user_h)
check('non-image payload rejected', res.status_code == 400, res.get_json().get('error', ''))
res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': b3['id'], 'screenshot_base64': '!!!not base64!!!'},
                  headers=user_h)
check('bad base64 rejected', res.status_code == 400, res.get_json().get('error', ''))
res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': b3['id']}, headers=user_h)
check('missing screenshot rejected', res.status_code == 400, res.get_json().get('error', ''))
res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': b3['id'], 'screenshot_base64': png_base64()},
                  headers=other_h)
check("cannot upload a screenshot for someone else's booking", res.status_code == 403)
res = anon.post('/api/payments/upi/upload-screenshot',
                json={'booking_id': b3['id'], 'screenshot_base64': png_base64()})
check('upload requires authentication', res.status_code == 401)
res = client.post('/api/payments/upi/upload-screenshot',
                  json={'booking_id': b2['id'], 'screenshot_base64': png_base64()},
                  headers=user_h)
check('upload blocked for a cancelled booking', res.status_code == 400,
      res.get_json().get('error', ''))

print('\n=== 9. Notification read state ===')
with app.app_context():
    admin_row = User.query.filter_by(email='admin@test.com').first()
    unread_before = Notification.query.filter_by(user_id=admin_row.id, is_read=False).count()
    check('admin has unread notifications before reading',
          unread_before >= 2, f'{unread_before} unread')
    nid = Notification.query.filter_by(user_id=admin_row.id, is_read=False).first().id

res = client.get('/api/notifications/unread-count', headers=admin_h)
check('unread-count endpoint works',
      res.status_code == 200 and res.get_json()['unread_count'] == unread_before,
      str(res.get_json()))
res = client.put(f'/api/notifications/{nid}/read', headers=admin_h)
check('mark read works',
      res.status_code == 200 and res.get_json()['unread_count'] == unread_before - 1,
      str(res.get_json()))
res = client.put(f'/api/notifications/{nid}/read', headers=user_h)
check("cannot mark another user's notification", res.status_code == 403)
res = client.put('/api/notifications/read-all', headers=admin_h)
check('mark all read works', res.status_code == 200)
res = client.get('/api/notifications/unread-count', headers=admin_h)
check('unread count back to zero', res.get_json()['unread_count'] == 0)

print('\n=== 10. Backwards compatibility ===')
with app.app_context():
    for code in ('C1', 'C2', 'C3'):
        s = Slot.query.filter_by(facility_id=facility_id, slot_code=code).first()
        s.is_occupied = False
        s.occupied_until = None
    db.session.commit()
res = make_booking(['C3'], ['MH03CC0003'], use_legacy=True)
check('legacy single vehicle_no still works', res.status_code == 201, res.get_json().get('error', ''))
check('legacy booking gets 1 vehicle', res.get_json()['booking']['vehicles'] == ['MH03CC0003'])

print('\n' + ('=' * 60))
if fails:
    print(f'{len(fails)} CHECK(S) FAILED:')
    for f in fails:
        print('  - ' + f)
    sys.exit(1)
print('ALL CHECKS PASSED')