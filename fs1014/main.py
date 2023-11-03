import os
import argparse

MemSize = 1000  # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.


class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name

        with open(os.path.join(ioDir, "imem.txt")) as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress):
        # read instruction memory
        # return 32 bit hex val

        binaryToHex = {"0000": '0', "0001": '1', "0010": '2', "0011": '3',
                       "0100": '4',
                       "0101": '5', "0110": '6', "0111": '7', "1000": '8',
                       "1001": '9',
                       "1010": 'A', "1011": 'B', "1100": 'C', "1101": 'D',
                       "1110": 'E', "1111": 'F'
                       }

        curr = ReadAddress

        instruction = ""
        hexInstruction = ""
        while (curr < ReadAddress + 4):
            instruction += str(self.IMem[curr])
            curr += 1

        for i in range(0, len(instruction), 4):
            hexInstruction += binaryToHex[instruction[i:i + 4]]

        print("Instruction", instruction)
        print("Hex Instruction", hexInstruction)

        return instruction


class DataMem(object):
    def __init__(self, name, input_path, output_path):
        self.id = name
        self.inDir = input_path
        self.outDir = output_path

        with open(os.path.join(self.inDir, "dmem.txt")) as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
        for i in range(len(self.DMem), MemSize):
            self.DMem.append('00000000')


    def readInstr(self, ReadAddress):
        # read data memory
        # return 32 bit hex val
        str_value = ""

        for i in range(4):
            str_value += self.DMem[ReadAddress + i]

        return str_value

    def writeDataMem(self, Address, WriteData):
        # write data into byte addressable memory

        binary_string = self.decimal_to_binary(WriteData)

        self.DMem[Address] = binary_string[0:8]
        self.DMem[Address + 1] = binary_string[8:16]
        self.DMem[Address + 2] = binary_string[16:24]
        self.DMem[Address + 3] = binary_string[24:32]

    def outputDataMem(self):
        resPath = os.path.join(self.outDir, f"{self.id}_DMEMResult.txt")
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

    def decimal_to_binary(self, num):
        all_bits = [0] * 32
        negative = False
        if num < 0:
            negative = True

        if num > pow(2, 31) - 1:
            num = (-1 * pow(2, 31)) + (num - (pow(2, 31)))
            negative = True

        elif num < -pow(2, 31):
            for i in range(2):
                num += pow(2, 31)
            negative = False

        num = abs(num)

        exponent = 31
        counter = 0
        while (num > 0):
            if pow(2, exponent) <= num:
                num -= pow(2, exponent)
                all_bits[counter] = 1
            exponent -= 1
            counter += 1

        if negative:
            for i in range(len(all_bits)):
                if all_bits[i] == 0:
                    all_bits[i] = 1
                else:
                    all_bits[i] = 0
            all_bits.reverse()
            all_bits[0] += 1

            # find carry
            for i in range(len(all_bits) - 1):
                if all_bits[i] == 2:
                    all_bits[i] = 0
                    all_bits[i + 1] += 1

            if all_bits[31] == 2:
                all_bits[31] = 0
            all_bits.reverse()

        bit_string = ""

        for bit in all_bits:
            bit_string += str(bit)

        return bit_string


class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = ['{:032b}'.format(0) for i in range(32)]

    def readRF(self, Reg_addr):
        # Fill in
        return self.Registers[Reg_addr]

    def writeRF(self, Reg_addr, Wrt_reg_data):
        # Fill in

        if Reg_addr == 0:
            return

        self.Registers[Reg_addr] = Wrt_reg_data

    def outputRF(self, cycle):
        op = ["-" * 70 + "\n",
              "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([str(val) + "\n" for val in self.Registers])
        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)


class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": False, "Instr": 0}
        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0,
                   "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "is_I_type": False,
                   "rd_mem": 0,
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0,
                    "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                    "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0,
                   "Wrt_reg_addr": 0, "wrt_enable": 0}


class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem


class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(os.path.join(ioDir, "SS_"),
                                              imem, dmem)
        self.opFilePath = os.path.join(ioDir, "StateResult_SS.txt")
        # self.decode = None
        self.decoded = None
        self.lastInstruction = None
        self.instruction_count = 0

    def instruction_fetch(self):
        PC_value = self.state.IF["PC"]
        return self.ext_imem.readInstr(PC_value)

    def string_to_decimal(self, s):
        sum = 0
        exponent = len(s) - 1

        for i in range(len(s)):
            if exponent == len(s) - 1:
                sum += -(pow(2, exponent) * int(s[i]))
            else:
                sum += (pow(2, exponent) * int(s[i]))
            exponent -= 1
        return sum


    def branch_immediate(self, immediate):
        """Method that returns the decimal value of the branch immediate."""
        bit_12 = immediate[0]
        bit_11 = immediate[11]
        bit_10_to_5 = immediate[1:7]
        bit_4_to_1 = immediate[7:11]

        ordered_immediate = bit_12 + bit_11
        ordered_immediate += bit_10_to_5
        ordered_immediate += bit_4_to_1
        ordered_immediate += "0"

        imm = self.string_to_decimal(ordered_immediate)

        return imm

    def jump_immediate(self, immediate):
        """Method that returns the decimal value of the jump immediate."""
        bit_20 = immediate[0]
        bit_19_to_12 = immediate[12:20]
        bit_11 = immediate[11]
        bit_10_to_5 = immediate[1:7]
        bit_4_to_1 = immediate[7:11]

        ordered_immediate = bit_20 + bit_19_to_12
        ordered_immediate += bit_11
        ordered_immediate += bit_10_to_5
        ordered_immediate += bit_4_to_1
        ordered_immediate += "0"

        imm = self.string_to_decimal(ordered_immediate)

        return imm

    def find_r_operation(self):
        '''Method that finds the specific r operation name.'''
        funct3 = self.decoded["funct3"]
        funct7 = self.decoded["funct7"]

        if funct3 == "000" and funct7 == "0000000":
            return "ADD"
        elif funct3 == "000" and funct7 == "0100000":
            return "SUB"
        elif funct3 == "100" and funct7 == "0000000":
            return "XOR"
        elif funct3 == "110" and funct7 == "0000000":
            return "OR"
        else:
            return "AND"

    def find_i_operation(self):
        '''Method that finds the specific i operation name.'''
        funct3 = self.decoded["funct3"]
        if funct3 == "000":
            return "ADDI"
        elif funct3 == "100":
            return "XORI"
        elif funct3 == "110":
            return "ORI"
        else:
            return "ANDI"


    def find_b_operation(self):
        '''Method that finds the specific branch operation name.'''
        funct3 = self.decoded["funct3"]
        if funct3 == "000":
            return "BEQ"
        else:
            return "BNE"

    def instruction_decode(self, instruction):
        self.state.ID["Instr"] = instruction
        opcode = instruction[25:32]

        # R Type
        if opcode == "0110011":
            print("R Type instruction.")
            self.decoded["opcode"] = opcode
            self.decoded["rd"] = self.string_to_decimal(instruction[20:25])
            self.decoded["funct3"] = instruction[17:20]
            self.decoded["rs1"] = self.string_to_decimal(instruction[12:17])
            self.decoded["rs2"] = self.string_to_decimal(instruction[7:12])
            self.decoded["funct7"] = instruction[0:7]
            self.decoded["type"] = "R"
            self.decoded["name"] = self.find_r_operation()

        elif opcode == "0010011":
            print("I Type instruction.")
            self.decoded["opcode"] = opcode
            self.decoded["rd"] = self.string_to_decimal(instruction[20:25])
            self.decoded["funct3"] = instruction[17:20]
            self.decoded["rs1"] = self.string_to_decimal(instruction[12:17])
            self.decoded["immediate"] = self.string_to_decimal(instruction[
                                                              0:12])
            self.decoded["type"] = "I"
            self.decoded["name"] = self.find_i_operation()

        elif opcode == "1101111":
            print("J type instruction.")
            self.decoded["opcode"] = opcode
            self.decoded["rd"] = self.string_to_decimal(instruction[20:25])
            immediate_bits = instruction[0:20]
            self.decoded["immediate"] = self.jump_immediate(immediate_bits)
            self.decoded["type"] = "J"
            self.decoded["name"] = "JAL"

        elif opcode == "1100011":
            print("B type instruction")
            self.decoded["opcode"] = opcode
            self.decoded["funct3"] = instruction[17:20]
            self.decoded["rs1"] = self.string_to_decimal(instruction[12:17])
            self.decoded["rs2"] = self.string_to_decimal(instruction[7:12])
            immediate_bits = instruction[0:7] + instruction[20:25]
            self.decoded["immediate"] = self.branch_immediate(immediate_bits)
            self.decoded["type"] = "B"
            self.decoded["name"] = self.find_b_operation()

        elif opcode == "0000011":
            print("Load instruction")
            self.decoded["opcode"] = opcode
            self.decoded["rd"] = self.string_to_decimal(instruction[20:25])
            self.decoded["funct3"] = instruction[17:20]
            self.decoded["rs1"] = self.string_to_decimal(instruction[12:17])
            self.decoded["immediate"] = self.string_to_decimal(instruction[
                                                              0:12])
            self.decoded["type"] = "I"
            self.decoded["name"] = "LW"

        elif opcode == "0100011":
            print("Store instruction")
            self.decoded["opcode"] = opcode
            self.decoded["funct3"] = instruction[17:20]
            self.decoded["rs1"] = self.string_to_decimal(instruction[12:17])
            self.decoded["rs2"] = self.string_to_decimal(instruction[7:12])
            self.decoded["immediate"] = self.string_to_decimal(instruction[
                                                             0:7] +
                                                             instruction[
                                                             20:25])
            self.decoded["type"] = "S"
            self.decoded["name"] = "SW"

        else:
            print("Halt instruction")
            self.decoded["type"] = "HALT"
            self.decoded["name"] = "HALT"
            self.state.IF["nop"] = True
            self.state.ID["nop"] = True

    def step(self):
        if self.decoded is None:
            self.decoded = dict()

        if self.lastInstruction is not None and "type" in \
                self.lastInstruction:
            print("type: ", self.lastInstruction["type"])
            if self.lastInstruction["type"] == "HALT":
                self.halted = True

        # Your implementation
        # 1. Instruction Fetch
        instruction = self.instruction_fetch()
        # Adder for the next PC.
        print(self.state.IF["PC"])

        # 2. Instruction Decode
        self.instruction_decode(instruction)
        print(self.decoded)

        # 3. Execute
        self.decoded["ALU_Result"] = None
        opname = self.decoded["name"]
        if opname == "ADD":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                + \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs2"]))
        elif opname == "SUB":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                - \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs2"]))
        elif opname == "XOR":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                ^ \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs2"]))
        elif opname == "OR":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"]))\
                | \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs2"]))
        elif opname == "AND":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                & \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs2"]))
        elif opname == "ADDI":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                + \
                self.decoded["immediate"]
        elif opname == "XORI":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                ^ \
                self.decoded["immediate"]
        elif opname == "ORI":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                | \
                self.decoded["immediate"]
        elif opname == "ANDI":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"]))\
                & \
                self.decoded["immediate"]
        elif opname == "JAL":
            self.decoded["ALU_Result"] = self.state.IF["PC"] + self.decoded[
                "immediate"]

        elif opname == "BEQ":
            rs1_value = self.string_to_decimal(self.myRF.readRF(self.decoded[
                                                                "rs1"]))
            rs2_value = self.string_to_decimal(self.myRF.readRF(
                self.decoded["rs2"]))

            if rs1_value == rs2_value:
                self.decoded["ALU_Result"] = self.state.IF["PC"] + \
                                             self.decoded["immediate"]
            else:
                self.decoded["ALU_Result"] = self.state.IF["PC"] + 4

        elif opname == "BNE":
            rs1_value = self.string_to_decimal(self.myRF.readRF(
                self.decoded["rs1"]))

            rs2_value = self.string_to_decimal(self.myRF.readRF(
                self.decoded["rs2"]))

            if rs1_value != rs2_value:
                self.decoded["ALU_Result"] = self.state.IF["PC"] + \
                                             self.decoded["immediate"]
            else:
                self.decoded["ALU_Result"] = self.state.IF["PC"] + 4

        elif opname == "LW":
            self.decoded["ALU_Result"] = self.string_to_decimal(
                self.myRF.readRF(self.decoded["rs1"])) \
                                         + \
                                         self.decoded["immediate"]
        elif opname == "SW":
            self.decoded["ALU_Result"] = \
                self.string_to_decimal(self.myRF.readRF(self.decoded["rs1"])) \
                + self.decoded["immediate"]
        else:
            self.decoded["ALU_Result"] = "HALT"

        # 4. Memory Access
        if opname == "LW":
            self.decoded["read_data"] = self.ext_dmem.readInstr(
                self.decoded["ALU_Result"])
        elif opname == "SW":
            self.ext_dmem.writeDataMem(self.decoded["ALU_Result"],
                                       self.string_to_decimal(self.myRF.readRF(
                                           self.decoded["rs2"])))

        print(self.decoded)
        # 5. Write Back
        if self.decoded["type"] == "R":
            binary_string = self.ext_dmem.decimal_to_binary(self.decoded[
                                                         "ALU_Result"])
            self.myRF.writeRF(self.decoded["rd"], binary_string)

        elif self.decoded["type"] == "I":
            if self.decoded["name"] == "LW":
                self.myRF.writeRF(self.decoded["rd"], self.decoded[
                    "read_data"])
            else:
                binary_string = self.ext_dmem.decimal_to_binary(self.decoded[
                    "ALU_Result"])
                self.myRF.writeRF(self.decoded["rd"], binary_string)
        elif self.decoded["type"] == "J":
            self.myRF.writeRF(self.decoded["rd"], self.ext_dmem.
                              decimal_to_binary(self.state.IF["PC"] + 4))


        # Update PC
        if self.decoded["type"] == "HALT":
            pass
        elif self.decoded["type"] == "R" or self.decoded["type"] == "I" or \
                self.decoded["type"] == "S":
            self.state.IF["PC"] += 4
        elif self.decoded["type"] == "B" or self.decoded["type"] == "J":
            self.state.IF["PC"] = self.decoded["ALU_Result"]

        # PRINTING
        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.state,
                        self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        # self.state = self.nextState  # The end of the cycle and updates the
        # current state with the values calculated in this cycle
        self.cycle += 1

        # update decoded instruction to last instruction.
        self.lastInstruction = self.decoded
        self.decoded = None

        if not self.halted:
            self.instruction_count += 1

    def printState(self, state, cycle):
        printstate = ["-" * 70 + "\n",
                      "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

    def printPerformanceMetrics(self):
        with open(os.path.join(self.ext_dmem.outDir,
                               "PerformanceMetrics.txt"), "w") as \
                file:
            file.write("Performance of Single Stage:\n")
            file.write("#Cycles -> " + str(self.cycle) + "\n")
            file.write("#Instructions -> " + str(self.instruction_count) +
                       "\n")
            CPI = self.cycle / self.instruction_count
            IPC = self.instruction_count / self.cycle
            file.write("CPI -> " + str(CPI) + "\n")
            file.write("IPC -> " + str(IPC) +"\n")

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(os.path.join(ioDir, "FS_"), imem, dmem)
        self.opFilePath = os.path.join(ioDir, "StateResult_FS.txt")


    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------

        # --------------------- MEM stage --------------------

        # --------------------- EX stage ---------------------

        # --------------------- ID stage ---------------------

        # --------------------- IF stage ---------------------

        self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX[
            "nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.nextState,
                        self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = self.nextState  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-" * 70 + "\n",
                      "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in
                           state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in
                           state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in
                           state.EX.items()])
        printstate.extend(
            ["MEM." + key + ": " + str(val) + "\n" for key, val in
             state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in
                           state.WB.items()])

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

    def printPerformanceMetrics(self):
        with open(os.path.join(self.ext_dmem.outDir, "PerformanceMetrics.txt"),"a") \
                as file:
            file.write("\nPerformance of Five Stage:\n")
            file.write("#Cycles -> " + str(self.cycle) + "\n")
            file.write("#Instructions -> \n")
            file.write("CPI -> \n")
            file.write("IPC -> \n")

if __name__ == "__main__":

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str,
                        help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    # main_path = os.path.dirname(ioDir)

    print("IO Directory:", ioDir)
    # print("Main Path:", main_path)

    input_path = os.path.join(ioDir, "input")
    print("Input Path:", input_path)
    output_path = os.path.join(ioDir, "output_fs1014")

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    print("Output Path:", output_path)

    for subdir, dirs, files in os.walk(input_path):
        for dir in dirs:
            update_input_path = input_path
            update_input_path = os.path.join(update_input_path, dir)
            update_output_path = output_path
            update_output_path = os.path.join(update_output_path, dir)

            print(update_output_path)

            if not os.path.exists(update_output_path):
                os.mkdir(update_output_path)

            imem = InsMem("Imem", update_input_path)
            dmem_ss = DataMem("SS", update_input_path, update_output_path)
            dmem_fs = DataMem("FS", update_input_path, update_output_path)
            print(update_input_path)
            print(update_output_path)

            ssCore = SingleStageCore(update_output_path, imem, dmem_ss)
            fsCore = FiveStageCore(update_output_path, imem, dmem_fs)

            while (True):
                if not ssCore.halted:
                    ssCore.step()

                if not fsCore.halted:
                    fsCore.step()

                if ssCore.halted and fsCore.halted:
                    break

            # dump SS and FS data mem.
            dmem_ss.outputDataMem()
            dmem_fs.outputDataMem()
            ssCore.printPerformanceMetrics()
            fsCore.printPerformanceMetrics()
