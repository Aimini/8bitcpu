import pathlib
import math
MICRO_CTL_LABEL = ["IRI", "IRHO", "IRLO",
                   "ROMO",
                   "PCO",
                   "PCCE",
                   "ADDRI",
                   "RAMI",
                   "RAMO",
                   "AI",
                   "AO",
                   "BI",
                   "BO",
                   "ALU_O",
                   "ALU_SUB",
                   "DII",
                   "HALT",
                   "RESERVED0",
                   "RESERVED1",
                   "PSWI", "PSW_IS",
                   "PCIS0","PCIS1","PCIS2"]

MICRO_CTL_ENCODE = {

}


mc_fetch = [["ROMO", "IRI", "PCCE"]]

mc = [
    ["NOP", ],  # 0000 - NOP
    ["LDA", ["IRLO", "ADDRI"], ["RAMO", "AI"]],  # 0001 - LDA
    ["ADD", ["IRLO", "ADDRI"], ["RAMO", "BI"], ["ALU_O", "AI", "PSWI", "PSW_IS"]],  # 0010 - ADD
    ["SUB", ["IRLO", "ADDRI"], ["RAMO", "BI"], ["ALU_O", "ALU_SUB", "AI", "PSWI", "PSW_IS"]],  # 0011 - SUB
    ["STA", ["IRLO", "ADDRI"], ["AO", "RAMI"]],  # 0100 - STA
    ["LDI", ["IRLO", "AI"]],  # 0101 - LDI
    ["JMP", ["IRLO","PCIS0"]],  # 0110 - JMP
    ["JC",  ["IRLO", "PCIS1"]],  # 0111 - JC
    ["JZ",  ["IRLO", "PCIS0","PCIS1"]],  # 1000 - JZ
    ["JOV", ["IRLO", "PCIS2"]],  # 1001 - JOV
    ["PSW", ["IRLO", "PSWI"]],  # 1010 - PSW
    [""],  # 1011
    [""],  # 1100
    [""],  # 1101
    ["OUT", ["AO", "DII"]],  # 1110 - output
    ["HALT",["HALT"]],  # 1111
]


directory = pathlib.Path("../eeprom-bin")

mcro_ctl_label_len = len(MICRO_CTL_LABEL)
eprom_num = int(math.ceil(mcro_ctl_label_len / 8))
print("using {} eeproms".format(eprom_num))
for idx, l in enumerate(MICRO_CTL_LABEL):
    v = 1 << idx
    MICRO_CTL_ENCODE[l] = v

    if idx % 4 == 0:
        print()
    print("{:>10}".format(l), end=' ')
    for i in reversed(range(2*eprom_num)):
        print("{:0>4b}".format(0xF & (v >> (i*4))), end=' ')
    print()

i = 0


def write_as_C(number):
    global i
    c = hex(number) + ","
    if i % 8 == 0:
        c += "\n"
    i += 1
    return c


def write_as_bin(number8bit):
   return (number8bit).to_bytes(length=1, byteorder='big')


def write_to_file(arr_bin, eprom_num, file, write_func):
    """
    write control bin to file, it will write one byte which in control signal intger value
    from low to high. 
    """
    for i in range(eprom_num):
        for instruction in arr_bin:
            for micro in instruction:
                file.write(write_func((micro >> (i*8)) & 0xFF))


def write_to_C(arr_bin, eprom_num):
    file = open(directory / "micro_code.c", 'w')
    file.write("code unsigned char array[] = {")
    write_to_file(arr_bin, eprom_num, file, write_as_C)

    file.write("};")
    file.close()


def write_to_Bin(arr_bin, eprom_num):
    file = open(directory / "micro_code.bin", 'bw')
    write_to_file(arr_bin, eprom_num, file, write_as_bin)
    file.close()


def dump_opcode(arr):
    with open("opcode_list.py", "w") as fh:
        fh.write("{")
        for idx, ins in enumerate(arr):
            name = ins[0]
            if name != '':
                fh.write('"{}":{},\n'.format(name, idx))
        fh.write("}")


def strip_op_name(arr):
    return [x[1:] for x in arr]


def append_fetch(arr):
    ret = []
    for x in arr:
        l = list(mc_fetch)
        l.extend(x)
        ret.append(l)
    return ret


def translate_labels_to_bin(arr, lut):
    """
    convert string label arrry to a single int.
    each instruction include multiple int control signal for each clock cycle.
    """
    bin_arr = []
    for instruction in arr:
        o = []
        for micros in instruction:
            control_combined = 0
            for label in micros:
                control_combined |= lut[label]
            o.append(control_combined)

        while len(o) < 8:
            o.append(0)

        bin_arr.append(o)

    return bin_arr


dump_opcode(mc)
mc = strip_op_name(mc)
mc = append_fetch(mc)
mc = translate_labels_to_bin(mc, MICRO_CTL_ENCODE)
write_to_Bin(mc, eprom_num)
