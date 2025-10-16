import unittest
import subprocess
import os

class TestBigHammer(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.join(self.test_dir, '..'))
        self.script_name = 'test_script.py'
        self.script_path = os.path.join(self.test_dir, self.script_name)
        # The fixture writes to /tmp/non-existing/test
        self.file_to_create_path = "/tmp/non-existing/test"

        # Copy the fixture to the test location
        fixture_path = os.path.join(self.test_dir, 'fixtures', 'test_script.py')
        with open(fixture_path, 'r') as f:
            script_content = f.read()

        with open(self.script_path, 'w') as f:
            f.write(script_content)

        # Ensure the directory and file don't exist before the test
        if os.path.exists(self.file_to_create_path):
            os.remove(self.file_to_create_path)
        if os.path.exists(os.path.dirname(self.file_to_create_path)):
            os.rmdir(os.path.dirname(self.file_to_create_path))

    def tearDown(self):
        # Clean up the created file and script
        if os.path.exists(self.file_to_create_path):
            os.remove(self.file_to_create_path)
        if os.path.exists(os.path.dirname(self.file_to_create_path)):
            try:
                os.rmdir(os.path.dirname(self.file_to_create_path))
            except OSError:
                pass  # Directory not empty or doesn't exist
        if os.path.exists(self.script_path):
            os.remove(self.script_path)

        fake_llm_path = os.path.join(self.test_dir, 'llm')
        if os.path.exists(fake_llm_path):
            os.remove(fake_llm_path)

        state_file = os.path.join(self.test_dir, 'llm_call_count')
        if os.path.exists(state_file):
            os.remove(state_file)

    def test_big_hammer_fixes_script(self):
        # Path to big-hammer
        big_hammer_path = os.path.join(self.project_root, 'big-hammer')
        
        # Create a fake `llm` that outputs the fixed version of the script.
        fake_llm_path = os.path.join(self.test_dir, 'llm')
        with open(fake_llm_path, 'w') as f:
            f.write("#!/bin/sh\n")
            # The "fixed" script content creates the directory and the file
            f.write("echo 'import os\n")
            f.write("os.makedirs(\"/tmp/non-existing\", exist_ok=True)\n")
            f.write("with open(\"/tmp/non-existing/test\", \"w\") as f:\n")
            f.write("    f.write(\"hello\")'\n")
        
        subprocess.run(['chmod', '+x', fake_llm_path], check=True)

        # Add the tests directory to the PATH so our fake llm is found
        env = os.environ.copy()
        env['PATH'] = self.test_dir + os.pathsep + env['PATH']

        # The command to run, with script path relative to project root
        command_to_run = [big_hammer_path, 'python3', os.path.join('tests', self.script_name)]
        
        result = subprocess.run(command_to_run, capture_output=True, text=True, env=env, cwd=self.project_root)

        # Assertions
        self.assertIn("Executing fixed script (attempt 1)", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertTrue(os.path.exists(self.file_to_create_path), f"File {self.file_to_create_path} was not created. Stderr: {result.stderr}, Stdout: {result.stdout}")

    def test_retry_succeeds_on_second_attempt(self):
        """Test that retry succeeds on the second attempt after first fix fails."""
        big_hammer_path = os.path.join(self.project_root, 'big-hammer')

        # Create a fake `llm` that alternates between a bad fix and a good fix
        # Use a state file to track whether this is the first or second attempt
        state_file = os.path.join(self.test_dir, 'llm_call_count')
        if os.path.exists(state_file):
            os.remove(state_file)

        fake_llm_path = os.path.join(self.test_dir, 'llm')
        with open(fake_llm_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"STATE_FILE='{state_file}'\n")
            f.write("# Consume stdin (required for llm tool)\n")
            f.write("cat > /dev/null\n")
            f.write("# Check if this is a retry by checking if state file exists\n")
            f.write("if [ -f \"$STATE_FILE\" ]; then\n")
            f.write("  # Second attempt - return working fix\n")
            f.write("  echo 'import os\n")
            f.write("os.makedirs(\"/tmp/non-existing\", exist_ok=True)\n")
            f.write("with open(\"/tmp/non-existing/test\", \"w\") as f:\n")
            f.write("    f.write(\"success\")'\n")
            f.write("else\n")
            f.write("  # First attempt - return broken fix and create state file\n")
            f.write("  touch \"$STATE_FILE\"\n")
            f.write("  echo 'import os\n")
            f.write("with open(\"/tmp/still-non-existing/test\", \"w\") as f:\n")
            f.write("    f.write(\"fail\")'\n")
            f.write("fi\n")

        subprocess.run(['chmod', '+x', fake_llm_path], check=True)

        # Add the tests directory to PATH
        env = os.environ.copy()
        env['PATH'] = self.test_dir + os.pathsep + env['PATH']

        # Run with --max-retries 2
        command_to_run = [big_hammer_path, '--max-retries', '2', 'python3', os.path.join('tests', self.script_name)]

        result = subprocess.run(command_to_run, capture_output=True, text=True, env=env, cwd=self.project_root)

        # Assertions
        self.assertIn("Attempt 1/2 failed. Retrying...", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertIn("Fix succeeded on attempt 2/2!", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertTrue(os.path.exists(self.file_to_create_path), f"File {self.file_to_create_path} was not created. Stderr: {result.stderr}, Stdout: {result.stdout}")
        self.assertEqual(result.returncode, 0, f"Expected exit code 0, got {result.returncode}")

    def test_all_retries_exhausted(self):
        """Test that all retries are exhausted and the command fails."""
        big_hammer_path = os.path.join(self.project_root, 'big-hammer')

        # Create a fake `llm` that always returns a broken fix
        fake_llm_path = os.path.join(self.test_dir, 'llm')
        with open(fake_llm_path, 'w') as f:
            f.write("#!/bin/sh\n")
            f.write("# Always return a broken fix that tries to write to a non-existent dir\n")
            f.write("echo 'import os\n")
            f.write("with open(\"/tmp/this-will-never-exist/test\", \"w\") as f:\n")
            f.write("    f.write(\"fail\")'\n")

        subprocess.run(['chmod', '+x', fake_llm_path], check=True)

        # Add the tests directory to PATH
        env = os.environ.copy()
        env['PATH'] = self.test_dir + os.pathsep + env['PATH']

        # Run with --max-retries 3
        command_to_run = [big_hammer_path, '--max-retries', '3', 'python3', os.path.join('tests', self.script_name)]

        result = subprocess.run(command_to_run, capture_output=True, text=True, env=env, cwd=self.project_root)

        # Assertions
        self.assertIn("Attempt 1/3 failed. Retrying...", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertIn("Attempt 2/3 failed. Retrying...", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertIn("All 3 attempt(s) exhausted. Unable to fix the problem.", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertNotEqual(result.returncode, 0, f"Expected non-zero exit code, got {result.returncode}")
        self.assertFalse(os.path.exists(self.file_to_create_path), f"File {self.file_to_create_path} should not exist")

if __name__ == '__main__':
    unittest.main()
