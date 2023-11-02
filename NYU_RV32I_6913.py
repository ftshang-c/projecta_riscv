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
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "\\dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in
                              dm.readlines()]
        for i in range(len(self.DMem), MemSize):
            self.DMem.append('00000000')


    def readInstr(self, ReadAddress):
        # read data memory
        # return 32 bit hex val
        str_value = ""

        for i in range(4):
            str_value += self.DMem[ReadAddress + 1]

        return str_value

    def writeDataMem(self, Address, WriteData):
        # write data into byte addressable memory

        binary_string = '{:032b}'.format(WriteData)
        stored_string = ""
        for character in binary_string:
            if character == "-":
                stored_string += "1"
            else:
                stored_string += character

        self.DMem[Address] = stored_string[0:8]
        self.DMem[Address + 1] = stored_string[8:16]
        self.DMem[Address + 2] = stored_string[16:24]
        self.DMem[Address + 3] = stored_string[24:32]

    def outputDataMem(self):
        resPath = self.ioDir + "\\" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])


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
        super(SingleStageCore, self).__init__(ioDir + "\\SS_", imem, dmem)
        self.decode = None
        self.opFilePath = ioDir + "\\StateResult_SS.txt"
        self.decoded = None
        self.lastInstruction = None

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
            self.decoded["rd"] = instruction[20:25]
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
        if not self.state.IF["nop"]:
            self.state.IF["PC"] += 4

        # 3. Execute
        self.decoded["ALU_Result"] = None
        self.decoded["PC_Adder"] = None
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
            pass
        elif opname == "BEQ":
            pass
        elif opname == "BNE":
            pass
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
            binary_string = '{:032b}'.format(self.decoded["ALU_Result"])
            self.myRF.writeRF(self.decoded["rd"], binary_string)
        elif self.decoded["type"] == "I":
            if self.decoded["name"] == "LW":
                self.myRF.writeRF(self.decoded["rd"], self.decoded[
                    "read_data"])
            else:
                self.myRF.writeRF(self.decoded["rd"], self.decoded[
                    "ALU_Result"])
        elif self.decoded["type"] == "B":
            pass
        elif self.decoded["type"] == "J":
            pass

        # PRINTING
        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.state,
                        self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        # self.state = self.nextState  # The end of the cycle and updates the
        # current state with the values calculated in this cycle
        self.cycle += 1
        self.lastInstruction = self.decoded
        self.decoded = None

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


class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "\\FS_", imem, dmem)
        self.opFilePath = ioDir + "\\StateResult_FS.txt"

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


if __name__ == "__main__":

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str,
                        help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)

    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)

    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

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