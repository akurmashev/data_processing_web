def parse_txt_file(filepath):
    with open(filepath, 'r') as file:
        return [float(line.strip()) for line in file]