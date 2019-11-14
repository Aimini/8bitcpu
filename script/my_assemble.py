import pathlib
directory =  pathlib.Path("../eeprom-bin")

def NOP():
    return 0

def LDA(addr:int):
    return 0x10 + addr

def ADD(addr:int):
    return 0x20 + addr

def SUB(addr:int):
    return 0x30 + addr

def STA(addr:int):
    return 0x40 + addr

def LDI(imed:int):
    return 0x50 + imed

def JMP(addr:int):
    return 0x60 + addr

def JC(addr:int):
    return 0x70 + addr

def JZ(addr:int):
    return 0x80 + addr 

def JOV(addr:int):
    return 0x90 + addr 

class PSW:
    __value = 0xA0
    def __init__(self,flag_index:int,value:bool):
        self.__value |= flag_index
        if value:
         self.__value |= 0x08
    
    def to_bytes(self,length,byteorder):
        return (self.__value).to_bytes(length=length, byteorder=byteorder)

    TCN = 0x01
    Cy = 0x20
    OV = 0x40

def OUT():
    return 0xE0

def HALT():
    return 0xF0

    



        
code = [
    PSW(PSW.TCN,False),
    LDI(1),
    STA(15),
    LDA(14),
    OUT(),
    ADD(15),
    JC(9),
    JMP(4),
    OUT(),
    SUB(15),
    JZ(4),
    JMP(8)   
]

def main():
    file = open(directory / "asm.bin",'bw')
    for x in code:
        file.write((x).to_bytes(length=1, byteorder='big'))
    file.close()    
    

main()