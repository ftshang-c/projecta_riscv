import unittest
from main import *

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        parser = argparse.ArgumentParser(description='RV32I processor')
        parser.add_argument('--iodir', default="", type=str,
                            help='Directory containing the input files.')
        args = parser.parse_args()

        ioDir = os.path.abspath(args.iodir)

        print("IO Directory:", ioDir)

        imem = InsMem("Imem", ioDir)
        dmem_ss = DataMem("SS", ioDir)
        dmem_fs = DataMem("FS", ioDir)

        self.ssCore = SingleStageCore(ioDir, imem, dmem_ss)
        self.fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    def test_string_to_decimal(self):
        actual = self.ssCore.string_to_decimal("1111111" + "11111")
        expected = -1
        self.assertEqual(actual, expected, "String To Decimal function did "
                                           "not convert correctly.")

        actual = self.ssCore.string_to_decimal("011111111110")
        expected = 2046
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

    def test_branch_immediate(self):
        actual = self.ssCore.branch_immediate("000000010000")
        expected = 16
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.branch_immediate("010000000000")
        expected = pow(2, 10)
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.branch_immediate("001000000000")
        expected = pow(2, 9)
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.branch_immediate("000000000001")
        expected = pow(2, 11)
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

    def test_jump_immediate(self):
        actual = self.ssCore.jump_immediate("00000001000000000000")
        expected = 16
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.jump_immediate("01000000000000000000")
        expected = pow(2, 10)
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.jump_immediate("00100000000000000000")
        expected = pow(2, 9)
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.jump_immediate("00000000000100000001")
        expected = 6144
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)

        actual = self.ssCore.jump_immediate("10000000000100000001")
        expected = -1042432
        message = "String to decimal function expected: " + str(expected) + \
                  "but actual: " + str(actual)
        self.assertEqual(actual, expected, message)


if __name__ == '__main__':
    unittest.main()