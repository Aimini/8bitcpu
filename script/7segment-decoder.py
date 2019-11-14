import pathlib

Dig = [0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xF8,0x80,0x90,0x88,0x83,0xc6,0xa1,0x86,0x8e,0xFF,0xBF]
anode = False

directory =  pathlib.Path("../eeprom-bin")

def write_digital(file,max,dig_gen):
    for i in range(max):
        c = Dig[dig_gen(i)]
        if anode is False:
            c = 0xFF - c
        file.write((c).to_bytes(length=1, byteorder='big'))


   
def write_two_complete(file,two = False):
    max = 256
    base = 1
    if two is False:
        while int(max / base) > 0: 
            write_digital(file,max,lambda x: int(x/base)%10)
            base *= 10
        write_digital(file,max,lambda x: -2)
    else:
        while int(max / base) > 0: 
            write_digital(file,max,lambda x: int((x if x < max/2  else max - x)/base)%10)
            base *= 10
        write_digital(file,max,lambda x: -1 if x > 127 else -2)

file = open(directory / "7seg.bin",'bw')
write_two_complete(file)
write_two_complete(file,True)
file.close()