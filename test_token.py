import subprocess, time, urllib.request, json, sys

proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)
time.sleep(3)

print('=== Testing Token Delivery ===')
print()

# Login
data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
req.add_header('Content-Type', 'application/json')
r = urllib.request.urlopen(req)
login_data = json.loads(r.read().decode())
token = login_data.get('access_token')
print('Token received:', token[:40] + '...')
print()

# Test 1: price-estimate (no @jwt_required)
print('1. Testing price-estimate (no auth required):')
est_data = {'facility_id': 1, 'vehicle_type': 'Car', 'duration_value': 2, 'duration_unit': 'hours', 'start_time': '2026-01-15T10:00:00'}
est_req = urllib.request.Request('http://127.0.0.1:5000/api/bookings/price-estimate', data=json.dumps(est_data).encode(), method='POST')
est_req.add_header('Content-Type', 'application/json')
est_req.add_header('Authorization', 'Bearer ' + token)
try:
    est_r = urllib.request.urlopen(est_req)
    print('   Works with Bearer token')
except Exception as e:
    print('   Failed with Bearer:', str(e)[:80])

# Test 2: create booking (has @jwt_required)
print()
print('2. Testing create booking (requires jwt_required):')
booking_data = {'facility_id': 1, 'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car', 'start_time': '2026-01-15T10:00:00', 'end_time': '2026-01-15T12:00:00', 'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}
book_req = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
book_req.add_header('Content-Type', 'application/json')
book_req.add_header('Authorization', 'Bearer ' + token)
try:
    book_r = urllib.request.urlopen(book_req)
    print('   Works with Bearer token')
except Exception as e:
    print('   Failed with Bearer:', str(e)[:80])
    # Try without auth
    book_req2 = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
    book_req2.add_header('Content-Type', 'application/json')
    try:
        book_r2 = urllib.request.urlopen(book_req2)
        print('   Works WITHOUT auth (unexpected)')
    except Exception as e2:
        print('   Also fails without auth')

# Stop server
proc.terminate()
print()
print('=== Done ===')