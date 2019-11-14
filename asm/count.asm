.data
count: 
.byte 0

.text
PSW 0x9
LDI 1        # A = 1
STA count    # count = A
LDI 0

PRINT_INC:
OUT
ADD count    # A += (1) count

JC  PRINT_DEC
JMP PRINT_INC

PRINT_DEC:
OUT
SUB count    # A -= (1) count
JZ  PRINT_INC
JMP PRINT_DEC