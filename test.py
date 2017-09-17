import time
import iqoption as iq

iqStream = iq.IQOption(active_id="BTCX")

print iqStream.getExpirationDateTime()
print iqStream.getServerDateTime()

while True:
    print 'result: '
    print iqStream.openPosition('call')
    time.sleep(0.5)