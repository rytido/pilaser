from subprocess import call
from time import sleep
from binascii import unhexlify, hexlify

def tohex(int_value):
    data_ = format(int_value, 'x')
    result = data_.rjust(4, '0')
    hexed = unhexlify(result)
    return hexed

t = r'echo"\x00\x00" > /dev/spidev0.0'

a = tohex(0)
b = tohex(100)
c = tohex(200)

l = [b"\x00\x00",
    b"\x38\xFF",
    b"\x16 \026",
    b"\x3d \075",
    b"\x7f \177",    
    b"\x3F\xFF"]


while True:
    for v in l:
        with open('/dev/spidev0.0', 'wb') as f:
            f.write(v)
        sleep(.01)
    for v in l:
        with open('/dev/spidev0.1', 'wb') as f:
            f.write(v)
        sleep(.01)
    for v in reversed(l):
        with open('/dev/spidev0.0', 'wb') as f:
            f.write(v)
        sleep(.01)
    for v in reversed(l):
        with open('/dev/spidev0.1', 'wb') as f:
            f.write(v)
        sleep(.01)     
    

