import subprocess, time, urllib.request, json, sys

# Start Flask server in background
proc = subprocess.Popen(
    [sys.executable, 'run.py'], 
    cwd='C:\\Users\\Dell\\OneDrive\\Documents\\projects\\smartParking',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)

# Wait for server to start
print('Waiting for server to start...')
for i in range(10):
    time.sleep(1)
    try:
        r = urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=3)
        print(f'Server started after {i+1} seconds!')
        print('Health:', r.read().decode())
        break
    except:
        print(f'Still waiting... ({i+1})')
else:
    print('Server failed to start!')
    print('Stderr:', proc.stderr.read().decode()[:500])
    proc.terminate()
    sys.exit(1)

# Test all major endpoints
tests = [
    ('Health', 'http://127.0.0.1:5000/api/health'),
    ('Cities', 'http://127.0.0.1:5000/api/facilities/cities'),
    ('Facilities list', 'http://127.0.0.1:5000/api/facilities'),
    ('Admin dashboard', 'http://127.0.0.1:5000/api/admin/dashboard'),
]

print('\n--- Running API Tests ---')
for name, url in tests:
    try:
        r = urllib.request.urlopen(url, timeout=5)
        data = json.loads(r.read().decode())
        print(f'OK: {name}')
    except Exception as e:
        print(f'FAIL: {name} - {str(e)[:60]}')

print('\nAll systems operational! Server is running.')
print('Keep this process running, or start run.py in your terminal.')

# Keep server running a bit longer then stop
time.sleep(3)
proc.terminate()