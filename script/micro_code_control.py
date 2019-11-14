import pathlib

IRI      = 0b000000000000000000000001
IRO      = 0b000000000000000000000010
IRLO     = 0b000000000000000000000100
PCI      = 0b000000000000000000001000
PCO      = 0b000000000000000000010000
PCCE     = 0b000000000000000000100000
ADDRI    = 0b000000000000000001000000
RAMI     = 0b000000000000000010000000
RAMO     = 0b000000000000000100000000
AI       = 0b000000000000001000000000
AO       = 0b000000000000010000000000
BI       = 0b000000000000100000000000
BO       = 0b000000000001000000000000
ALU_O    = 0b000000000010000000000000
ALU_SUB  = 0b000000000100000000000000
DII      = 0b000000001000000000000000
HALT     = 0b000000010000000000000000
DO       = 0b000000100000000000000000
DPTRI    = 0b000001000000000000000000
PSWI     = 0b000010000000000000000000
PSW_IS   = 0b000100000000000000000000
mc = [
    [PCO | DPTRI, DO | IRI | PCCE,              0,         0,                          0, 0, 0, 0], # 0000 - NOP
    [PCO | DPTRI, DO | IRI | PCCE,   IRLO | ADDRI, RAMO | AI,                          0, 0, 0, 0], # 0001 - LDA
    [PCO | DPTRI, DO | IRI | PCCE,   IRLO | ADDRI, RAMO | BI,           ALU_O | AI| PSWI | PSW_IS, 0, 0, 0], # 0010 - ADD 
    [PCO | DPTRI, DO | IRI | PCCE,   IRLO | ADDRI, RAMO | BI,  ALU_O| ALU_SUB | AI| PSWI | PSW_IS, 0, 0, 0],# 0011 - SUB
    [PCO | DPTRI, DO | IRI | PCCE,   IRLO | ADDRI, AO | RAMI,                          0, 0, 0, 0],# 0100 - STA
    [PCO | DPTRI, DO | IRI | PCCE,      IRLO | AI,         0,                          0, 0, 0, 0],# 0101 - LDI
    [PCO | DPTRI, DO | IRI | PCCE,     IRLO | PCI,         0,                          0, 0, 0, 0],# 0110 - JMP
    [PCO | DPTRI, DO | IRI | PCCE,     IRLO | PCI,         0,                          0, 0, 0, 0],# 0111 - JC
    [PCO | DPTRI, DO | IRI | PCCE,     IRLO | PCI,         0,                          0, 0, 0, 0],# 1000 - JZ
    [PCO | DPTRI, DO | IRI | PCCE,     IRLO | PCI,         0,                          0, 0, 0, 0],# 1001 - JOV
    [PCO | DPTRI, DO | IRI | PCCE,    IRLO | PSWI,         0,                          0, 0, 0, 0],# 1010 - PWS
    [PCO | DPTRI, DO | IRI | PCCE,              0,         0,                          0, 0, 0, 0],# 1011
    [PCO | DPTRI, DO | IRI | PCCE,              0,         0,                          0, 0, 0, 0],# 1100
    [PCO | DPTRI, DO | IRI | PCCE,              0,         0,                          0, 0, 0, 0],# 1101
    [PCO | DPTRI, DO | IRI | PCCE,       AO | DII,         0,                          0, 0, 0, 0],# 1110 - OUT
    [PCO | DPTRI, DO | IRI | PCCE,           HALT,         0,                          0, 0, 0, 0],# 1111
]       
       


directory =  pathlib.Path("../eeprom-bin")
i = 0
def write_as_C(number):
    c = hex(number) + ","
    if i%8 == 0:
        c += "\n"
    i += 1
    return c


def write_as_bin(number8bit):
   return (number8bit).to_bytes(length=1, byteorder='big')

def write_to_file(file,write_func):
    for instruction in mc:
        for micro in instruction:
            file.write(write_func(micro & 0xFF))
            
        
    for instruction in mc:
        for micro in instruction:
            file.write(write_func(micro>>8 & 0xFF))
            

    for instruction in mc:
        for micro in instruction:
            file.write(write_func(micro>>16 & 0xFF))

def write_to_C():
    file = open(directory / "micro_code.c",'w')
    file.write("code unsigned char array[] = {")
    write_to_file(file,write_as_C)

    file.write("};")
    file.close()

def write_to_Bin():
    file = open(directory / "micro_code.bin",'bw')
    write_to_file(file,write_as_bin)
    file.close()

write_to_Bin()