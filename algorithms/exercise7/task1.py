def main():
    n, m = map(int, input().split())
    matrix = [list(map(int, input().split())) for i in range(n)]
    for i in range(n):
        for j in range(m):
            up = 0
            left = 0
            if i - 1 >= 0:
                up = matrix[i - 1][j]
            if j - 1 >= 0:
                left = matrix[i][j - 1]
            matrix[i][j] += max(up, left)

    print(matrix[n - 1][m - 1])


if __name__ == "__main__":
    main()