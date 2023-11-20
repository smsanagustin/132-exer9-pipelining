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
        instruction.append(0) # counter of stages
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

# start of pipelining
instructions_count = len(instructions)
stages = ["F", "D", "E", "M", "W"]
added_space = False
write_registers = []
read_dict = {}

# appropriate stage will be appended to each instruction
for i in range(len(instructions)):
    data_hazard = False
    current_instruction = instructions[i]
    checked_hazards = False
    
    # get read and write registers for this instruction
    
    write = current_instruction[2] # stores the register that the current instruction writes on
    write_registers.append(write) # add to list of write registers
    read = [] # tracks registers being read by the current instruction
    for k in range(3, 5):
        read.append(current_instruction[k])
        
    # save read registers to dictionary to track read registers of each instruction
    read_dict[i] = read
    
    while True:
        print("i: " + str(i))
        # if current instruction already reached writeback, move to the next instruction
        if current_instruction[0] == 5: 
            break
        
        j = current_instruction[0] # stage counter
        current_instruction.append(stages[j]) # fetch or get the next instruction
        current_instruction[0] += 1 # increment stage counter
         
        # after first fetch, next instruction can proceed with fetching (if it exists)
        if (i + 1) < instructions_count:
            next_instruction = instructions[i+1]
            if j == 1:
                # adds space for the succeding instructions
                if not added_space:
                    for k in range((i+1), len(instructions)):
                        # add space on the left k times
                        for l in range(k):
                            instructions[k].append("-")
                        added_space = True
                
                next_instruction.append(stages[0]) # append fetch
                next_instruction[0] += 1 # increment stage counter of next instruction
            elif j == 0:
                if not checked_hazards:
                    instructions_to_wait = [] # stores the indices of instructions to wait for
                    # check if there are data hazards
                    write_register = next_instruction[2]
                    if write_register == write: # write after write
                        data_hazard = True    
                        instructions_to_wait.append(i)
                    elif write_register in read: # write after read
                        data_hazard = True
                        instructions_to_wait.append(i) 
                        
                    # data hazard in instructions other than the current
                    else: 
                        # read after write in this instructions and others
                        for k in range(3, 5):
                            if next_instruction[k] in write_registers:
                                data_hazard = True
                                # find the register that it needs to wait for
                                for index in range(len(write_registers)):
                                    if write_registers[index] == next_instruction[k]:
                                        wait_for = index
                                        instructions_to_wait.append(wait_for)
                            if next_instruction[k] == write: # read after write
                                data_hazard = True
                                instructions_to_wait.append(i)
                                break
                            
                        # write after write in other instructions
                        for index in range(len(write_registers)):
                            if write_registers[index] == next_instruction[2]:
                                wait_for = index
                                instructions_to_wait.append(wait_for)
                                data_hazard = True
                            
                        # write after read in other instructions
                        for key in read_dict.keys(): 
                            print(read_dict[key])
                            print(write_register)
                            if write_register in read_dict[key]:
                                wait_for = key
                                instructions_to_wait.append(wait_for)
                                data_hazard = True
                        
                    checked_hazards = True
            else:
                # if there are data hazards, stall next instruction until current instruction writesback
                if data_hazard:
                    next_instruction.append("S") # stall
                    
                    # if next instruction waits for current instruction then wait
                    if i in instructions_to_wait:
                        if current_instruction[0] == 5:
                            # next instruction can start decoding
                            next_instruction.append(stages[1])
                            next_instruction[0] += 1 # increment stage counter
                    else:
                        # check if instructions to wait has finished writeback
                        for index in range(len(instructions_to_wait)):
                            if instructions[index][0] != 5: # stage count is 5 (W)
                                data_hazard = True
                                break
                            data_hazard = False
                         
                        # if instructions to wait has finished writing
                        # and current instruction has finished decoding then
                        # decode next instruction
                        if current_instruction[0] > 1 and not data_hazard:
                            next_instruction.append(stages[1]) # decode
                            next_instruction[0] += 1 # increment next instruction's stage counter
                else:
                    # if there are no data hazards, run 5 stage cycle as normal
                    stage_index = next_instruction[0]
                    next_instruction.append(stages[stage_index])
                    next_instruction[0] += 1 # increment next instruction's stage counter
        j += 1 # move to the next stage

output_file = open("output.txt", "w")
column_width = 4
for instruction in instructions:
    for i in range(1, len(instruction)):
        if i == 1:
            to_write = instruction[i] + " "
            output_file.write("{:<{}}".format(to_write, column_width))
        elif i < 3:
            to_write = instruction[i] + ", "
            output_file.write("{:<{}}".format(to_write, column_width))
        else:
            to_write = instruction[i]
            output_file.write("{:<{}}".format(to_write, column_width))
    output_file.write("\n")
        
print(data_hazard) 
output_file.close()