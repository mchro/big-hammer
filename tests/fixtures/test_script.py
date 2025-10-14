#!/usr/bin/python

import os

def main():
    file_to_read = "/tmp/non-existing/test"
    
    print(f"Attempting to read '{{file_to_read}}'...")
    
    with open(file_to_read, 'r') as f:
        content = f.read()
        print("File content:")
        print(content)

if __name__ == "__main__":
    main()
