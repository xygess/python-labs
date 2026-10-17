def main():
    num = int(input())
    result = True
    if num < 0:
        result = False
    else:
        digits = []
        while num != 0:
            digits.append(num % 10)
            num //= 10
        for i in range(len(digits) // 2):
            if digits[i] != digits[-(i + 1)]:
                result = False
    print(result)


if __name__ == "__main__":
    main()