def main():
    first = map(float, input().split())
    second = map(float, input().split())
    result = 0.0

    for x, y in zip(first, second):
        result += (x * y)

    print(result)

if __name__ == "__main__":
    main()