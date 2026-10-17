def main():
    try:
        n = int(input())
    except ValueError:
        return print('Natural number was expected')
    pascal = []
    for i in range(n):
        if i == 0:
            pascal.append([1])
        else:
            pascal.append([])
            for j in range(i + 1):
                if j == 0:
                    pascal[i].append(pascal[i - 1][j])
                else:
                    pascal[i].append(sum(pascal[i - 1][j - 1:j + 1]))
        print(*pascal[i])


if __name__ == "__main__":
    main()