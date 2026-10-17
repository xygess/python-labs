def main():
    try:
        n, time = map(int, input().split())
    except ValueError:
        return print("Incorrect input")
    if n <= 0 or time <= 0:
        return print("Incorrect input")
    groups = {}
    result = None
    for _ in range(n):
        try:
            year, cost, t = map(int, input().split())
        except (ValueError, EOFError):
            return print("Incorrect input")
        if year <= 0 or cost <= 0 or t <= 0:
            return print("Incorrect input")
        groups[year] = groups.get(year, {})
        if time - t in groups[year]:
            current_cost = cost + groups[year][time - t]
            if result is not None:
                result = min(result, current_cost)
            else:
                result = current_cost
        groups[year][t] = min(groups[year].get(t, cost), cost)
    print(result)

if __name__ == "__main__":
    main()