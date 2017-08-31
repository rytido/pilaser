from subprocess import call
from time import sleep
from binascii import unhexlify, hexlify

def tohex(v):
    return unhexlify("%0.4X" % (v+4096))

t = r'echo -ne "\x00\x00" > /dev/spidev0.0'

open('/dev/spidev0.0', 'wb').write(b'\x10\x00')
open('/dev/spidev0.0', 'wb').write(tohex(0))
#range seems to be x10x00 to x17xFF

j=48
t=.001
open('/dev/spidev0.0', 'wb').write(tohex(0))
open('/dev/spidev0.1', 'wb').write(tohex(0))
l1 = range(0, 2048, j)
l2 = reversed(l1)
while True:
    for x in range(0, 2048, j):
        open('/dev/spidev0.0', 'wb').write(tohex(x))
        sleep(t)
    for x in range(0, 2048, j):
        open('/dev/spidev0.1', 'wb').write(tohex(x))
        sleep(t)
    for x in reversed(range(0, 2048, j)):
        open('/dev/spidev0.0', 'wb').write(tohex(x))
        sleep(t)                
    for x in reversed(range(0, 2048, j)):
        open('/dev/spidev0.1', 'wb').write(tohex(x))
        sleep(t)    

