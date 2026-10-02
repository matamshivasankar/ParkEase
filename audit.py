src = open('frontend/js/main.js', encoding='utf-8').read()
# functions referenced in markup/handlers that must exist
import re
defined = set(re.findall(r'^\s{2}(?:async )?function (\w+)', src, re.M)) | set(re.findall(r'^  const (\w+) =', src, re.M))
called = set(re.findall(r'\b(joinBookingRoom|toggleNotifPanel|resetNotifications|connectSocket|disconnectSocket|checkPaymentStatus|startPaymentPolling|renderPendingVerification|updateVehicleValidity|validateVehicles|readVehicleNumbers|renderVehicleInputs|loadAdminVerifications|openVerifyScreenshot|verifyScreenshotAction|adminTab|onNotifClick)\(', src))
print('missing helpers:', sorted(called - defined))
print()
print('vehicleDrafts as array?', 'vehicleDrafts = [' in src)
print('payload has vehicle_nos:', 'vehicle_nos:' in src)
print('slot_count sent:', 'slot_count:' in src)
