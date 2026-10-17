def main():
    n, x = input().split()
    n = int(n)
    x = float(x)
    result = 0
    for i in range(n, 0, -1):
        result += float(input()) * i * x ** (i - 1)
    _ = float(input())
    print(f"{result:.3f}")


if __name__ == "__main__":
    main()