# Architecture
## register
this 8 bit CPU have two core Register  `A` and `PSW`. 
when excute instruction load data form memory/immed or arithmatic operation, `A` always store the reulst of excute, when the instcution take two operand, `A`was used as one operand.
`PSW` is a 4bit register, it's store flag when execute arithmatic instruction, it's also control the output port display style.
|bit|00|01|10|11|
|:-:|:-:|:-:|:-:|:-:|
|name|NOP|LDA|ADD|SUB|
|name|NOP|LDA|ADD|SUB|
## IO
we only have one output port to display sinle byte number, execute OUT instruction will send data to output port.

## RAM
4x4(64bit) sram

## PC
only 4bit address, 16 instructions only. each instcution take 8 cycles.

# ISA Overview
CPU using IR[7:4] as instruction encoding field. the data in IR[3:0] will use as operand in some instruction.
|encode|00|01|10|11|
|:-:|:-:|:-:|:-:|:-:|
|00|NOP|LDA|ADD|SUB|
|01|STA|LDI|JMP|JC|
|10|JZ|JOV|PSW||
|11|||OUT||

# Detail
## NOP
|0000|0000|
|:-:|:-:|
Do nothing, just consume cycle.

## LDA
|0001|addr|
|:-:|:-:|
load nibble byte form `addr` to `A`

## ADD
|0010|addr|
|:-:|:-:|
add value in `A` and value in `addr`,sotre result in `A`.

> affected flag:  OV, CARRY


## SUB
|0011|addr|
|:-:|:-:|
subtract value in `A` and value in `addr`,sotre result in `A`.

> affected flag:  OV, CARRY

## STA
|0100|addr|
|:-:|:-:|
store value in `A` to `addr`

## LDI
|0101|immed|
|:-:|:-:|
load nibble byte `immed` to `A`, high 4 bit in `A` will be set to 0.

## JMP
|0110|addr|
|:-:|:-:|
jump to `addr`.

## JC
|0111|addr|
|:-:|:-:|
jump to `addr` when `PSW.CY`.


## JZ
|1000|addr|
|:-:|:-:|
jump to `addr` when `A` is 0.

## JOV
|1001|addr|
|:-:|:-:|
jump to `addr` when `PSW.OV`.


## PSW
|1010|immed|
|:-:|:-:|
set `PSW` to `immed`.

## OUT
|1110|xxxx|
|:-:|:-:|
send `A` to ouput port.