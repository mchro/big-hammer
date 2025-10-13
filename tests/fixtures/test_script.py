import os

def main():
    # This file does not exist, which will cause an error.
    file_to_read = "{file_to_create_name}"
    
    print(f"Attempting to read '{{file_to_read}}'...")
    
    with open(file_to_read, 'r') as f:
        content = f.read()
        print("File content:")
        print(content)

if __name__ == "__main__":
    main()
