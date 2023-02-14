import os
import sys

def main():
    with open(sys.argv[1]) as f:
        lines = f.readlines()

    def question(q):
        return input(q).lower().strip()[0] == "y" or question(q)

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if question(f"Are you sure to delete {line}? "):
            os.remove(line)
