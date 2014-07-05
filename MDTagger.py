import sys
import os

folder_name = sys.argv[1]
print folder_name

is_directory = os.path.isdir(folder_name)

if not is_directory:
    print "Parameter must be a directory"
    quit()

directory_list = os.listdir(folder_name)

for filename in directory_list:
    full_file_path = os.path.join(folder_name, filename)
    if os.path.isfile(full_file_path):
        print full_file_path

