
import os
from os.path import isfile, join


data_folder = "/Users/tlazauskas/git/Turing/reginald/data/handbook/"

onlyfiles = [f for f in os.listdir(data_folder) if isfile(join(data_folder, f))]
for f in onlyfiles:
    print(f)    

# file_path = "/Users/tlazauskas/git/Turing/reginald/data/handbook/overtime.md"
# content = read_markdown_file(file_path)