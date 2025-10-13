import unittest
import subprocess
import os

class TestBigHammer(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.join(self.test_dir, '..'))
        self.script_name = 'test_script.py'
        self.script_path = os.path.join(self.test_dir, self.script_name)
        self.file_to_create_name = "non_existent_file.txt"
        self.file_to_create_path = os.path.join(self.project_root, self.file_to_create_name)

        # Create the failing script for each test
        fixture_path = os.path.join(self.test_dir, 'fixtures', 'test_script.py')
        with open(fixture_path, 'r') as f:
            script_template = f.read()
        
        script_content = script_template.format(file_to_create_name=self.file_to_create_name)

        with open(self.script_path, 'w') as f:
            f.write(script_content)

        # Ensure the file that the script needs does not exist before the test
        if os.path.exists(self.file_to_create_path):
            os.remove(self.file_to_create_path)

    def tearDown(self):
        # Clean up the created file and script
        if os.path.exists(self.file_to_create_path):
            os.remove(self.file_to_create_path)
        if os.path.exists(self.script_path):
            os.remove(self.script_path)
        
        fake_llm_path = os.path.join(self.test_dir, 'llm')
        if os.path.exists(fake_llm_path):
            os.remove(fake_llm_path)

    def test_big_hammer_fixes_script(self):
        # Path to big-hammer
        big_hammer_path = os.path.join(self.project_root, 'big-hammer')
        
        # Create a fake `llm` that outputs the fixed version of the script.
        fake_llm_path = os.path.join(self.test_dir, 'llm')
        with open(fake_llm_path, 'w') as f:
            f.write("#!/bin/sh\n")
            # The "fixed" script content is just creating the file.
            f.write(f"echo 'with open(\"{self.file_to_create_name}\", \"w\") as f:\\n    f.write(\"hello\")'\n")
        
        subprocess.run(['chmod', '+x', fake_llm_path], check=True)

        # Add the tests directory to the PATH so our fake llm is found
        env = os.environ.copy()
        env['PATH'] = self.test_dir + os.pathsep + env['PATH']

        # The command to run, with script path relative to project root
        command_to_run = [big_hammer_path, 'python3', os.path.join('tests', self.script_name)]
        
        result = subprocess.run(command_to_run, capture_output=True, text=True, env=env, cwd=self.project_root)

        # Assertions
        self.assertIn("LLM suggested a fix", result.stdout, f"Stdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertTrue(os.path.exists(self.file_to_create_path), f"File {self.file_to_create_path} was not created. Stderr: {result.stderr}, Stdout: {result.stdout}")

if __name__ == '__main__':
    unittest.main()
