import scipy.io

def parse_mat_file(filepath):
    data = scipy.io.loadmat(filepath)
    return data