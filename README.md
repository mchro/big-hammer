# big-hammer

*"If it fails, you should have used a bigger hammer."*

`big-hammer` is a command-line tool that acts as a smart wrapper around any script. If the script fails (i.e., exits with a non-zero status code), `big-hammer` will use an LLM to analyze the error and automatically generate and execute a command to fix the problem.

## Features

-   Wraps any executable command (shell scripts, Python, etc.).
-   Automatically detects script failures.
-   Uses the powerful `llm` command-line tool to generate a fix based on the script's source code, exit code, stdout, and stderr.
-   Executes the suggested fix in a temporary, non-destructive way.
-   The original script is never modified.

## Prerequisites

Before using `big-hammer`, you must have the `llm` command-line tool installed. This tool is used to interact with large language models from the command line.

You can install it by following the official instructions:
[https://llm.datasette.io/en/stable/installation.html](https://llm.datasette.io/en/stable/installation.html)

After installation, make sure to configure it with an API key for a model provider (e.g., OpenAI, Anthropic, Google).

## Installation

1.  Place the `big-hammer` script in your desired directory.
2.  Make it executable:
    ```bash
    chmod +x big-hammer
    ```
3.  (Optional) Move it to a directory in your `PATH` for system-wide access:
    ```bash
    sudo mv big-hammer /usr/local/bin/
    ```

## Usage

To use `big-hammer`, simply prepend it to the command you want to run.

### Example

Let's say you have a Python script `test_script.py` that tries to read a file that doesn't exist:

**test_script.py:**
```python
import os

def main():
    # This file does not exist, which will cause an error.
    file_to_read = "non_existent_file.txt"
    
    print(f"Attempting to read '{file_to_read}'...")
    
    with open(file_to_read, 'r') as f:
        content = f.read()
        print("File content:")
        print(content)

if __name__ == "__main__":
    main()
```

Running this script directly will fail:
```bash
$ python3 test_script.py
Attempting to read 'non_existent_file.txt'...
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'non_existent_file.txt'
```

Now, run it with `big-hammer`:
```bash
./big-hammer python3 test_script.py
```

**What Happens:**

1.  `big-hammer` executes `python3 test_script.py`.
2.  It captures the `FileNotFoundError` and the non-zero exit code.
3.  It constructs a detailed prompt with the script's source code and all the error details.
4.  It sends the prompt to the `llm` tool.
5.  The LLM will likely return a fix, such as `touch non_existent_file.txt`.
6.  `big-hammer` will create a temporary shell script containing this fix and execute it.

The output will look something like this:
```
>>> Executing command: python3 test_script.py
>>> Command failed. Asking LLM for a fix...
>>> LLM suggested a fix. Executing it from /tmp/tmpXXXXXX.sh...
--------------------
# Output from the fix script will be shown here
--------------------
>>> Fix execution finished.
```

## Customization

### Changing the LLM Model

By default, `big-hammer` uses the `gpt-4o` model. You can specify a different model using the `-m` or `--model` flag.

```bash
./big-hammer -m gpt-3.5-turbo python3 your_script.py
```
This will pass the `-m gpt-3.5-turbo` argument directly to the `llm` utility.
