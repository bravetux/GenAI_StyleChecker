def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def validate_file_path(file_path):
    import os
    return os.path.isfile(file_path) or os.path.isdir(file_path)

def get_all_cs_files(directory):
    import os
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.cs')]