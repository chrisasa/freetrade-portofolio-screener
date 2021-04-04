import os
import subprocess


def reset():
    clear()

def clear():
    if os.name in ('nt', 'dos'):
        subprocess.call("cls")
    elif os.name in ('linux', 'osx', 'posix'):
        subprocess.call("clear")
    else:
        print("\n" * 120)

def clear_file(file_path):
    open(file_path, 'w+').close()

def append(txt, out_file):
    with open(out_file, 'a') as f:
        f.write( '\n' + str(txt) )

def file_exists(filename):
    return os.path.isfile(filename)
