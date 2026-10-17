def main():
    n = int(input())
    unique = set()
    for _ in range(n):
        unique.add(int(input()))
    print(len(unique))


if __name__ == "__main__":
    main()