import json


def validate_data(data):
    if (type(data) != dict
        or 'list1' not in data or 'list2' not in data
        or type(data['list1']) != list or type(data['list2']) != list
        or any(type(el) != dict for el in data['list1'])
        or any('title' not in el for el in data['list1'])
        or any('year' not in el for el in data['list1'])
        or any(type(el['title']) != str for el in data['list1'])
        or any(type(el['year']) != int for el in data['list1'])
        or any(type(el) != dict for el in data['list2'])
        or any('title' not in el for el in data['list2'])
        or any('year' not in el for el in data['list2'])
        or any(type(el['title']) != str for el in data['list2'])
        or any(type(el['year']) != int for el in data['list2'])):
        return 1


def merge_sort(data, output):
    j = 0
    for i in range(len(data['list1'])):
        while len(data['list2']) != j and data['list1'][i]['year'] > data['list2'][j]['year']:
            output['list0'].append(data['list2'][j])
            j += 1
        output['list0'].append(data['list1'][i])
    for i in range(j, len(data['list2'])):
        output['list0'].append(data['list2'][i])


def main():
    with open("src/exercise6/input.txt", "r") as file:
        content = file.read()
    if not content.strip():
        return print("Empty file")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return print("Incorrect file")
    
    output = {'list0': []}
    if validate_data(data):
        return print('Incorrect data')
    
    merge_sort(data, output)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()