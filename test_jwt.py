import subprocess, time, urllib.request, json, sys
from urllib.error import HTTPError

proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)
time.sleep(3)

print('=== JWT Configuration Test ===')
print()

# Login and get token
data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
req.add_header('Content-Type', 'application/json')
r = urllib.request.urlopen(req)
login_data = json.loads(r.read().decode())
token = login_data.get('access_token')
print('1. Login token:', token[:50] + '...')
print()

# Test price-estimate (no jwt_required needed)
print('3. price-estimate (no auth required):')
est_data = {'facility_id': 1, 'vehicle_type': 'Car', 'duration_value': 2, 'duration_unit': 'hours', 'start_time': '2026-01-15T10:00:00'}
est_req = urllib.request.Request('http://127.0.0.1:5000/api/bookings/price-estimate', data=json.dumps(est_data).encode(), method='POST')
est_req.add_header('Content-Type', 'application/json')
est_req.add_header('Authorization', 'Bearer ' + token)
try:
    est_r = urllib.request.urlopen(est_req)
    print('   Works with Bearer token')
except Exception as e:
    print('   Failed with Bearer token:', str(e)[:80])

# Test create_booking with Bearer token
print()
print('4. create_booking (has jwt_required):')
booking_data = {'facility_id': 1, 'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car', 'start_time': '2026-01-15T10:00:00', 'end_time': '2026-01-15T12:00:00', 'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}
book_req = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
book_req.add_header('Content-Type', 'application/json')
book_req.add_header('Authorization', 'Bearer ' + token)
try:
    book_r = urllib.request.urlopen(book_req)
    print('   Works with Bearer token')
except HTTPError as e:
    print('   Failed with Bearer token: HTTP Error', e.code)
    body = e.read().decode()
    print('   Response:', body[:200])

# Test: check JWT error details
print()
print('6. Check actual JWT error:')
book_req6 = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
book_req6.add_header('Content-Type', 'application/json')
try:
    book_r6 = urllib.request.urlopen(book_req6)
except HTTPError as e:
    print('   HTTP Status:', e.code)
    body = e.read().decode()
    print('   Response body:', body[:300])

proc.terminate()
print()
print('=== Done ===')