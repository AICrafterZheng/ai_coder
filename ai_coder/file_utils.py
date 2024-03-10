
# In this function, `filename` is the name of the file you want to write to, and `content` is the string that you want to write. 
# The 'w' parameter in `open` function means that the file is opened for writing. If the file already exists, it is truncated. If it does not exist, it is created.
# Please note that this function will overwrite the file if it already exists. If you want to append to the file instead, change 'w' to 'a' in the `open` function.
def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

# append to the file
def append_file(filename, content):
    with open(filename, 'a') as f:
        f.write(content)

# read from the file
def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()