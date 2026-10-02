import subprocess, time, urllib.request, json, sys

# Start Flask server
proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)

# Wait for server
time.sleep(3)

print('=== Testing Booking Flow ===')
print()

# Step 1: Login
print('1. Logging in...')
try:
    data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
    req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    r = urllib.request.urlopen(req)
    login_data = json.loads(r.read().decode())
    token = login_data.get('access_token')
    print('   Login successful')
    print('   Token:', token[:30] + '...')
except Exception as e:
    print('   Login failed:', str(e)[:100])
    proc.terminate()
    exit(1)

# Step 2: Get price estimate
print()
print('2. Getting price estimate...')
try:
    est_data = {
        'facility_id': 1,
        'vehicle_type': 'Car',
        'duration_value': 2,
        'duration_unit': 'hours',
        'start_time': '2026-01-15T10:00:00'
    }
    est_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    est_req = urllib.request.Request(
        'http://127.0.0.1:5000/api/bookings/price-estimate', 
        data=json.dumps(est_data).encode(), 
        method='POST'
    )
    est_req.add_header('Content-Type', 'application/json')
    est_req.add_header('Authorization', 'Bearer ' + token)
    est_r = urllib.request.urlopen(est_req)
    price_data = json.loads(est_r.read().decode())
    pbd = price_data.get('price_breakdown', {})
    print('   Price estimate OK')
    print('   Base:', pbd.get('base_price'), 'Discount:', pbd.get('discount'), 'Total:', pbd.get('total_amount'))
except Exception as e:
    print('   Price estimate error:', str(e)[:150])

# Step 3: Try to create booking
print()
print('3. Creating booking...')
try:
    booking_data = {
        'facility_id': 1,
        'vehicle_no': 'MH12AB1234',
        'vehicle_type': 'Car',
        'start_time': '2026-01-15T10:00:00',
        'end_time': '2026-01-15T12:00:00',
        'duration_value': 2,
        'duration_unit': 'hours',
        'slot_codes': ['C1', 'C2']
    }
    book_req = urllib.request.Request(
        'http://127.0.0.1:5000/api/bookings', 
        data=json.dumps(booking_data).encode(), 
        method='POST'
    )
    book_req.add_header('Content-Type', 'application/json')
    book_req.add_header('Authorization', 'Bearer ' + token)
    book_r = urllib.request.urlopen(book_req)
    booking = json.loads(book_r.read().decode())
    bid = booking.get('booking', {}).get('booking_id', 'N/A')
    status = booking.get('booking', {}).get('status', 'N/A')
    total = booking.get('booking', {}).get('total_amount', 'N/A')
    print('   Booking created:', bid)
    print('   Status:', status)
    print('   Total amount:', total)
except Exception as e:
    print('   Booking creation error:', str(e)[:200])
    import traceback
    traceback.print_exc()

# Stop server
proc.terminate()
print()
print('=== Test Complete ===')