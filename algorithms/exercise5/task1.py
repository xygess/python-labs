def process_sign(number, fsm):
    if number and number[0] == '+':
        number = number[1:]
    elif number and number[0] == '-':
        fsm['sign'] = -1
        number = number[1:]
    return number


def read_number(number, fsm):
    for i in number:
        if i.isdigit():
            fsm['digit_found'] = True
            if not fsm['dot']:
                fsm['integer'] *= 10
                fsm['integer'] += ord(i) - ord('0')
            else:
                fsm['len_mantissa'] += 1
                fsm['mantissa'] *= 10
                fsm['mantissa'] += ord(i) - ord('0')
        elif i == '.' and not fsm['dot']:
            fsm['dot'] = True
        else:
            return 1


def build_number(fsm):
    num = fsm['integer'] + fsm['mantissa'] / 10 ** fsm['len_mantissa']
    return num if fsm['sign'] == 1 else -num


def main():
    number = input()
    fsm = {'sign': 1,
           'integer': 0,
           'len_mantissa': 0,
           'mantissa': 0,
           'dot': False,
           'digit_found': False}
    number = process_sign(number, fsm)
    if read_number(number, fsm) or not fsm['digit_found']:
        return print('A number is expected')
    float_number = build_number(fsm)
    print(f"{float_number * 2:.3f}")


if __name__ == "__main__":
    main()