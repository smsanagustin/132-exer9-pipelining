file1 = open("instruction.txt", "r")

instructions = []
opcodes = ["add", "mul", "sub", "div"]
operands_list = []
lines = file1.readlines()

# get instructions from input file
for line in lines:
    # store here the current instruction (opcode, 3 operands)
    instruction = []

    # get the opcode
    opcodes_and_operands = line.strip().split(" ")

    # get the opcode
    opcode = opcodes_and_operands[0]

    # if the opcode is a valid opcode, proceed with getting the operands
    if opcode not in opcodes:
        print("Invalid opcode!")
        exit()
    else:
        instruction.append(opcode)
        for i in range(1, 4):
            operand = opcodes_and_operands[i]
            operand = operand.strip(",")
            # check if operand is valid (in number of registers)
            if int(operand[1:len(operand)]) in range(0, 16):
                instruction.append(operand) # get operands
            else:
                print(operand, "is invalid!")
                exit()
        instructions.append(instruction)
        
file1.close()

print(instructions)