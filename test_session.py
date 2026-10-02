import subprocess, time, urllib.request, urllib.error, json, sys

proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)
time.sleep(3)

# Login and follow redirects to get cookies
print('1. Logging in...')
data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    r = urllib.request.urlopen(req, timeout=5)
    print('   Login successful, response code:', r.status)
except urllib.error.HTTPError as e:
    print('   Login failed: HTTP Error', e.code)
    proc.terminate()
    exit(1)

# Now try create_booking WITHOUT explicit auth header (cookies should be sent automatically by urllib if redirect maintained them)
# But urllib doesn't auto-send cookies between separate requests unless we use a cookie jar
# Let me try a different approach - use the health check first to verify session

print()
print('2. Testing session via health check:')
req2 = urllib.request.Request('http://127.0.0.1:5000/api/health')
try:
    r2 = urllib.request.urlopen(req2, timeout=5)
    print('   Health check OK:', r2.read().decode()[:50])
except urllib.error.HTTPError as e:
    print('   Health check failed:', e.code)

# Try create_booking - maybe the session from login persists?
print()
print('3. Testing create_booking with same urllib session:')
booking_data = {'facility_id': 1, 'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car', 'start_time': '2026-01-15T10:00:00', 'end_time': '2026-01-15T12:00:00', 'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}
book_req = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
book_req.add_header('Content-Type', 'application/json')
try:
    book_r = urllib.request.urlopen(book_req, timeout=5)
    booking = json.loads(book_r.read().decode())
    bid = booking.get('booking', {}).get('booking_id', 'N/A')
    print('   Booking created:', bid)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print('   Failed: HTTP Error', e.code)
    print('   Response:', body[:200])

proc.terminate()
print()
print('=== Done ===')