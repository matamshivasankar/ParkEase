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

# Test: Login as demo user to get token
try:
    # First login
    data = json.dumps({'email': 'demo@parkease.com', 'password': 'Demo@123'}).encode()
    req = urllib.request.Request('http://127.0.0.1:5000/api/auth/login', data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    r = urllib.request.urlopen(req)
    login_data = json.loads(r.read().decode())
    token = login_data.get('access_token')
    print('Login successful, token:', token[:50] + '...')
    
    # Test: Create a booking
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
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
    req = urllib.request.Request('http://127.0.0.1:5000/api/bookings', data=json.dumps(booking_data).encode(), method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    r = urllib.request.urlopen(req)
    booking_response = json.loads(r.read().decode())
    print('Booking created:', booking_response.get('booking', {}).get('booking_id', 'N/A'))
    print('Status:', booking_response.get('booking', {}).get('status', 'N/A'))
    print('Price breakdown:', booking_response.get('price_breakdown', {}))
    
except Exception as e:
    print(f'Error: {e}')
    if proc.stderr:
        err = proc.stderr.read().decode()[:500]
        print('Server stderr:', err)

# Stop server
proc.terminate()