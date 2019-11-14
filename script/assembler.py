from io import StringIO
import re
import enum
import pathlib
import sys

"""
1. read all line and strip blank char at line head and end
2. tokenize all line, evaluate all integer value
3. iter each line's token, 
    * assign label's address
    * generate ram data
    * generate instruction
        - for instruction with immed, or label already have address, just convert it's to binary byte, then save it to corresponding address
        - for instruction with unresolved label, add it to a list, we will process it at next step
3. generate instruction with unresolved label again
        
4 .write text/data segment to binary file

4.convert text/data segment to binary file
"""


class segment_assigner:
    """
    assign data to appropriate address in appropriate segment
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pc = [0]  # program counter
        self.dc = [0]  # data counter
        self.counter = self.pc  # indcate current counter; default is pc
        self.in_text = True

        # address:int -> value: byte
        self.data = {}
        self.text = {}
        self.current_segment = self.text

    def segdata(self):
        self.counter = self.dc
        self.in_text = False
        self.current_segment = self.data

    def segtext(self):
        self.counter = self.pc
        self.in_text = True
        self.current_segment = self.text

    def inc(self):
        self.counter[0] += 1

    def set_counter(self, val):
        self.counter[0] = val

    def get_counter(self):
        return self.counter[0]

    def set_value(self, val):
        address = self.get_counter()
        if self.text:
            etext = "text"
        else:
            etext = "data"

        if self.current_segment.get(address) is not None:
            print("[error]", etext, "segment overlapped at address", address)
            return -1
        self.current_segment[address] = val
        self.inc()
        return 0


ac = segment_assigner()
# name:string -> address:int
label_map = {

}

opcode_map = {

}

opcode_file = pathlib.Path(sys.argv[0]).parent / "opcode_list.py"
with open(opcode_file) as fh:
    opcode_map = eval(''.join(fh.readlines()))


def process_directive(se):
    """

    """
    d = se[0]
    global ac
    # text segment
    if d == '.text' or d == '.data':
        if d == '.text':
            ac.segtext()
        else:
            ac.segdata()
        if len(se) >= 2:
            ac.set_counter(se[1])

    # set explicity data in segment
    elif d == '.byte':
        data = se[1]

        if len(se) < 2:
            print("[error]", "no value assign to byte directive")
            return -1
        # error when set value to segment
        r = ac.set_value(data & 0xFF)
        if r != 0:
            return r

        if data > 255:
            print("[warn]data {} exceed 255, truncted to 8-bit const {}.".format(data, data & 0xFF))
            return 1

    else:
        print("[error]", "unkonw directive ", d)
        return -1
    return 0


def process_label(se):
    """
    convert label to absolute address
    """
    l = se[0][:-1]
    address = ac.get_counter()
    if label_map.get(l) is not None:
        print('[error]redefine label "{}"'.format(l))
        return -1
    label_map[l] = address
    if len(se) > 1:
        print('[warn] there some content after the label "{}", you must wrap a newline.'.format(l))
        return 1
    return 0


def process_instruction(se, line):
    instruction = se[0]
    opcode = 0
    try:
        opcode = opcode_map[instruction.upper()]
        if opcode > 15:
            print("[error]{}'s opcode {} too large".format(instruction, opcode))
            return -1
    except KeyError as e:
        print("[error]unknow token", instruction)
        return -1
    opcode <<= 4

    operand_value = 0
    if len(se) > 1:
        operand_token = se[1]
        # it's  a number, check range ,then combine opcode to an byte
        if isinstance(operand_token, int):
            operand_value = operand_token
         # not a number, maybe a label
        else:
            label_value = label_map.get(operand_token)
            if label_value is not None:
                operand_value = label_value
            else:  # maybe we can get label value after processed all tokenized line
                  # we will try to get label value again in write binary process
                ac.inc()
                return 2

    ac.set_value(opcode | (operand_value & 0xFF))
    if operand_value > 15:
        print("[warn]opearnd {} exceed 15, truncted to 4-bit const.".format(operand_value))
        return -1

    return 0


def tokenize_line(line):
    """
    line:text string in a line

    strip blank char
    remove comment
    split string to token
    convert string to int
    """
    #remove comment
    s = line.split('#')[0]
    s = [x for x in re.split('[\\s,]', s) if len(x) > 0]
    ret = []
    for one in s:
        # check first char, reduce exception cost
        if one[0].isdigit():
            try:
                ret.append(int(one, 0))
            except:
                ret.append(one)
        else:
            ret.append(one)
    return ret


def assembler_label(address_lines):
    """
    resolve label address again after assembler done
    """
    ac.segtext()
    for pc, idx, line_str, statement in address_lines:
        ac.set_counter(pc)
        result = process_instruction(statement, idx)
        if result != 0:
            print('"{}" at line {}'.format(line_str, idx + 1))


def assembler(file):
    lines = file.readlines()
    lines = [x.strip() for x in lines]
    assembler_label_tokenized_lines = []
    """
        preprocess assembler, maybe some instuction won't resolve label address at these time.
    """
    for idx, statement in enumerate([tokenize_line(x.strip()) for x in lines]):
        if len(statement) <= 0:
            continue
        op0 = statement[0]
        result = 0
        # it's a directive
        if op0.startswith('.'):
            result = process_directive(statement)

        #it's a label
        elif op0.endswith(':'):
            result = process_label(statement)
        else:

            l = [ac.get_counter(), idx, lines[idx]]
            result = process_instruction(statement, idx)
            if result == 2:
                l.append(statement)
                assembler_label_tokenized_lines.append(l)
        if result != 0 and result != 2:
            print('"{}" at line {}'.format(lines[idx], idx + 1))

    assembler_label(assembler_label_tokenized_lines)


def write_one_segment(filename, mem_map):
    mem_data = sorted(mem_map.items(), key=lambda x: x[0])
    first = 0
    last = 0
    if len(mem_data) > 0:
        first = mem_data[0][0]
        last = mem_data[-1][0]
    binary_datas = bytearray(last + 1)
    for a, v in mem_data:
            binary_datas[a] = v

    with open(filename, "wb") as fh:
        print(filename)
        fh.write(binary_datas)


def write_file(filename_prefix):
   write_one_segment(filename_prefix + "data.bin", ac.data)
   write_one_segment(filename_prefix + "text.bin", ac.text)


test = False
if test:
    assembler(StringIO("""
.data
count: 
.byte 11
.byte 12

.data 0xFF
.byte 12312


.text
PSW
LDI 1
STA 15
LDA 14

PRINT_INC:
OUT
ADD 15
JC  PRINT_DEC
JMP PRINT_INC

PRINT_DEC:
OUT
SUB 15
JZ  PRINT_INC
JMP PRINT_DEC
"""))
else:
    file = pathlib.Path(sys.argv[1])
    
    outputdir = file.parent
    try:  
         outputdir = pathlib.Path(sys.argv[2])
    except:
        pass


    outfilename = file.stem
    try:
        outfilename = sys.argv[3]
    except:
        pass
    

    with open(file) as fhandle:
        assembler(fhandle)
    
    write_file(str(outputdir /(outfilename +'.' )))
