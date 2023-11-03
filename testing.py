#
# x = "1000000" + "00000"
# sum = 0
# exponent = len(x) - 1
#
# for i in range(len(x)):
#     if exponent == len(x) - 1:
#         sum += -(pow(2, exponent) * int(x[i]))
#     else:
#         sum += (pow(2, exponent) * int(x[i]))
#     exponent -= 1
#
# print(sum)
#
#

def decimal_to_binary(num):
    all_bits = [0] * 32
    negative = False
    if num < 0:
        negative = True

    if num > pow(2, 31) - 1 or num < -pow(2, 31):
        return

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

decimal_to_binary(25)
decimal_to_binary(-pow(2, 31) + 1)
print(abs(-25))
# print(result[0:8])
