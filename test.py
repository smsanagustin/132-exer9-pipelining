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
    if opcode.lower() not in opcodes:
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
 
# get all write and read registers
write_registers = []
read_registers = {} # key = index, value = list of registers
for i in range(len(instructions)):
    write_registers.append(instructions[i][1])
   
    read_list = [] 
    for j in range(2,4):
        read_list.append(instructions[i][j])
        read_registers[i] = read_list
    
# check for data hazards per instruction
data_hazards = {} # key: index of the instruction; value: index of instruction to wait for

for i in range(1, len(instructions)):
    write = instructions[i][1]
    read = []
    for j in range(2,4):
        read.append(instructions[i][j])
        
    # indices of instructions to wait for
    instructions_to_wait_for = []
    
    # write after write
    for k in range(i):
        if not (i == k) and write == write_registers[k]:
            instructions_to_wait_for.append(k)
    
    # write after read
    for k in range(i):
        if not (i == k) and write in read_registers[k]:
            instructions_to_wait_for.append(k)
    
    # read after write
    for reg in read:
        for k in range(i):
            if not (k == i) and reg == write_registers[k]:
                instructions_to_wait_for.append(k)
        
    data_hazards[i] = instructions_to_wait_for

# perform 5 stage cycle for all instructions
stages = ["F", "D", "E", "M", "W"]
for i in range(len(instructions)):
    stage_count = 0
    current_instruction = instructions[i]
    n = i + 1
    if i == 0: # perform 5 stage cycle on the first instruction
        for j in range(len(stages)):
            stage = stages[j]
            current_instruction.append(stage)
        if n < len(instructions):
            next_instruction = instructions[n]
            next_instruction.append("-") 
    else:
        prev_instruction = instructions[i-1]
        current_instruction.append("F")
        # next instruction waits n times
        if n < len(instructions):
            next_instruction = instructions[n]
            for j in range(n):
                next_instruction.append("-")
                
        # if no data hazards, perform 5 stage cycle w/out stall
        if not data_hazards[i]:
            # check first if the previous instruction has finished decoding
            start = 4 + i
            for j in range(start, len(prev_instruction)):
                if prev_instruction[j] == "D":
                    current_instruction.append("D")
                    break
                else:
                    current_instruction.append("S")
                    
            # perform other instructions
            for j in range(2, len(stages)):
                current_instruction.append(stages[j])
        else: # if there are data hazards, wait for instructions to finish
            start = 5 + i
            max_index = max(data_hazards[i]) # wait only for the nearest instruction
            for j in range(start, len(instructions[max_index])):
                stage = instructions[max_index][j]
                current_instruction.append("S")
 
            # check first if the previous instruction has finished decoding
            start = 4 + i
            for j in range(start, len(prev_instruction)):
                if prev_instruction[j] == "D":
                    current_instruction.append("D")
                    break
                else:
                    current_instruction.append("S")
            # perform other stages after stalling
            for j in range(2, len(stages)):
                current_instruction.append(stages[j])
             
                        
output_file = open("output.txt", "w")
column_width = 4
for instruction in instructions:
    for i in range(len(instruction)):
        if i == 0:
            to_write = instruction[i] + " "
            output_file.write("{:<{}}".format(to_write, column_width))
        elif i < 2:
            to_write = instruction[i] + ", "
            output_file.write("{:<{}}".format(to_write, column_width))
        else:
            to_write = instruction[i]
            output_file.write("{:<{}}".format(to_write, column_width))
    output_file.write("\n")
        
output_file.close()

print(data_hazards)