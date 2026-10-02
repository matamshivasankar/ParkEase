import subprocess, time, urllib.request, urllib.error, urllib.parse, http.cookiejar, json, sys

proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)
time.sleep(3)

print('=== Testing with Cookie Jar ===')
print()

# Create cookie jar to maintain session
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: Login
print('1. Logging in...')
data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
req.add_header('Content-Type', 'application/json')
try:
    r = opener.open(req, timeout=5)
    login_data = json.loads(r.read().decode())
    print('   Login successful')
    print('   Cookies set:', len(cj.cookies))
except Exception as e:
    print('   Login failed:', str(e)[:80])
    proc.terminate()
    exit(1)

# Step 2: Get token from cookies
print()
print('2. Checking cookies:')
for cookie in cj.cookies:
    print('   Cookie:', cookie.name, '=', cookie.value[:30] if len(cookie.value) > 30 else cookie.value)

# Step 3: Create booking using cookies (no explicit Bearer header)
print()
print('3. Creating booking using cookies:')
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
    print('   Total:', total)
except urllib.error.HTTPError as e:
    print('   Failed: HTTP Error', e.code)
    body = e.read().decode()
    print('   Response:', body[:200])

# Step 4: Try with Bearer header + cookies
print()
print('4. Creating booking with Bearer header + cookies:')
booking_data2 = {'facility_id': 1, 'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car', 'start_time': '2026-01-15T10:00:00', 'end_time': '2026-01-15T12:00:00', 'duration_value': 2, 'duration_unit': 'hours', 'slot_codes': ['C1']}
book_req2 = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data2).encode(), method='POST')
book_req2.add_header('Content-Type', 'application/json')
# Get the access token cookie value
access_token = cj.cookies.get('parkease_access_token', type=http.cookiejar.Cookie).value if 'parkease_access_token' in cj.cookies else ''
book_req2.add_header('Authorization', 'Bearer ' + access_token if access_token else 'Bearer none')
try:
    book_r2 = opener.open(book_req2, timeout=5)
    print('   Works with Bearer + cookies')
except urllib.error.HTTPError as e:
    print('   Failed: HTTP Error', e.code)
    body = e.read().decode()
    print('   Response:', body[:200])

proc.terminate()
print()
print('=== Done ===')