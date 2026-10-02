import subprocess, time, urllib.request, urllib.error, http.cookiejar, json, sys

proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)
time.sleep(3)

print('=== Testing Booking Creation ===')
print()

# Use opener that maintains cookies
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: Login
print('1. Logging in...')
data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    r = opener.open(req, timeout=5)
    print('   Login successful')
except urllib.error.HTTPError as e:
    print('   Login failed: HTTP Error', e.code)
    proc.terminate()
    exit(1)

# Check what cookies were set
print('   Cookies:')
for cookie in cj.cookies:
    print('   -', cookie.name, '=', cookie.value[:40])

# Step 2: Create booking using opener (cookies sent automatically)
print()
print('2. Creating booking (using cookie-based auth):')
booking_data = {'facility_id': 1, 'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car', 'start_time': '2026-01-15T10:00:00', 'end_time': '2026-01-15T12:00:00', 'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}
book_req = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
book_req.add_header('Content-Type', 'application/json')
try:
    book_r = opener.open(book_req, timeout=5)
    booking = json.loads(book_r.read().decode())
    bid = booking.get('booking', {}).get('booking_id', 'N/A')
    status = booking.get('booking', {}).get('status', 'N/A')
    total = booking.get('booking', {}).get('total_amount', 'N/A')
    print('   Booking created:', bid)
    print('   Status:', status)
    print('   Total amount:', total)
except urllib.error.HTTPError as e:
    print('   Failed: HTTP Error', e.code)
    body = e.read().decode()
    print('   Response:', body[:300])

# Step 3: Try with explicit Bearer header ON TOP of cookies
print()
print('5. Creating booking with explicit Bearer header:')
booking_data2 = {'facility_id': 1, 'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car', 'start_time': '2026-01-15T10:00:00', 'end_time': '2026-01-15T12:00:00', 'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}
book_req2 = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data2).encode(), method='POST')
book_req2.add_header('Content-Type', 'application/json')
# Get token from cookies and add Bearer header
for cookie in cj.cookies:
    if cookie.name == 'parkease_access_token':
        book_req2.add_header('Authorization', 'Bearer ' + cookie.value)
        print('   Added Bearer header with token:', cookie.value[:30] + '...')
        break

try:
    book_r2 = opener.open(book_req2, timeout=5)
    booking = json.loads(book_r2.read().decode())
    bid = booking.get('booking', {}).get('booking_id', 'N/A')
    print('   Booking created with Bearer header:', bid)
except urllib.error.HTTPError as e:
    print('   Failed: HTTP Error', e.code)
    body = e.read().decode()
    print('   Response:', body[:300])

proc.terminate()
print()
print('=== Done ===')