from xbee import ZigBee
from xbee.helpers.dispatch import Dispatch
import serial
import struct
import time
import os

PORT = os.getenv('XBEE_PORT', '/dev/ttyAMA0')
BAUD_RATE = 9600
HUB_ADDR = struct.pack('>Q', 0) # 64-bit 0s
BCAST_ADDR = '\xFF\xFE'

IS_HUB = bool(os.getenv('IS_HUB'))

def default_handler(name, packet):
    print "%s - %s" % (name, packet)

def at_response_handler(name, packet):
    p = ''.join('%02x' % ord(x) for x in packet['parameter'])
    print "AT - %s = %s" % (packet['command'], p)
    
def rx_handler(name, packet):
    print "RX - %s" % packet
    time.sleep(1)
    data = "PONG" if IS_HUB else "PING"
    zb.tx(dest_addr_long=packet['source_addr_long'], dest_addr=packet['source_addr'], data=data)
        

ser = serial.Serial(PORT, BAUD_RATE)
zigbee = ZigBee(ser)
dispatch = Dispatch(xbee = zigbee)
dispatch.register('rx', rx_handler, lambda p: p['id'] == 'rx')
dispatch.register('rx_explicit', default_handler, lambda p: p['id'] == 'rx_explicit')
dispatch.register('rx_io_data_long_addr', default_handler, lambda p: p['id'] == 'rx_io_data_long_addr')
dispatch.register('tx_status', default_handler, lambda p: p['id'] == 'tx_status')
dispatch.register('status', default_handler, lambda p: p['id'] == 'status')
dispatch.register('at_response', at_response_handler, lambda p: p['id'] == 'at_response')
dispatch.register('remote_at_response', default_handler, lambda p: p['id'] == 'remote_at_response')
dispatch.register('node_id_indicator', default_handler, lambda p: p['id'] == 'node_id_indicator')

zb = ZigBee(ser, callback = dispatch.dispatch, escaped = True)

print "run..."
print ""
print "current status:"
zb.send('at', command='ID')
zb.send('at', command='SH')
zb.send('at', command='SL')
zb.send('at', command='MY')
print ""

time.sleep(1)

print ""
if not IS_HUB:
    print "edge node - send frame to %s" % HUB_ADDR
    zb.tx(dest_addr_long=HUB_ADDR, dest_addr=BCAST_ADDR, data="PING")
else:
    print "hub node - waiting for data"
    
while True:
    try:
        time.sleep(2)
    except KeyboardInterrupt:
        break

zb.halt()
    
# try:
#     print "run..."
#     dispatch.run()
# except KeyboardInterrupt:
#     pass

ser.close()
