def detect_figure(visited, figure, row, col, directions, matrix):
    stack = [(row, col)]
    while stack:
        row, col = stack.pop()
        if (row, col) in visited:
            continue
        visited.add((row, col))
        figure.add((row, col))
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            if ((0 <= new_row < len(matrix) and 0 <= new_col < len(matrix))
                and matrix[new_row][new_col] == 1
                and (new_row, new_col) not in visited):
                stack.append((new_row, new_col))


def classify_figure(figure, figures):
    rows = {row for row, _ in figure}
    cols = {col for _, col in figure}
    height = max(rows) - min(rows) + 1
    width = max(cols) - min(cols) + 1
    if height * width == len(figure):
        figures["square"] += 1
    else:
        figures["circle"] += 1


def main():
    visited = set()
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    figures = {"square": 0, "circle": 0}

    with open("src/exercise3/input.txt", "r") as file:
        matrix = [list(map(int, line.split())) for line in file]

    for row in range(len(matrix)):
        for col in range(len(matrix)):
            if matrix[row][col] == 1 and (row, col) not in visited:
                figure = set()
                detect_figure(visited, figure, row, col, directions, matrix)
                classify_figure(figure, figures)
    print(figures["square"], figures["circle"])


if __name__ == "__main__":
    main()