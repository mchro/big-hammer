#!/usr/bin/python

import os

def main():
    file_to_write_to = "/tmp/non-existing/test"
    
    print(f"Attempting to write to '{{file_to_read}}'...")
    
    with open(file_to_write_to, 'w') as f:
        f.write("DEBUG OUTPUT: 42")

if __name__ == "__main__":
    main()
