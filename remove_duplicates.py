# Removes duplicate lines from a file
# Usage: python remove_duplicates.py <file>

import sys

def remove_duplicates(file):
    lines = set()
    for line in file:
        lines.add(line)
    return lines

if __name__ == '__main__':
    file = open(sys.argv[1], 'r')
    lines = remove_duplicates(file)
    file.close()
    # write to file
    file = open(sys.argv[1] + ".new.txt", 'w')
    for line in lines:
        file.write(line)
    file.close()