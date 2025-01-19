from datetime import datetime

def parse_txt_file(filepath):
    """
    Parses a .txt file containing timepoints and returns them as a list of floats.
    """
    timepoints = []
    with open(filepath, 'r') as file:
        for line in file:
            try:
                timepoints.append(line.strip())
            except ValueError as e:
                raise ValueError(f"Invalid value in file {filepath}: {line.strip()}") from e
    return timepoints

