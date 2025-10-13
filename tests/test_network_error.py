import unittest
import subprocess
import os

class TestNetworkError(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(__file__)
        self.project_root = os.path.abspath(os.path.join(self.test_dir, '..'))
        self.script_name = 'test_curl_503.sh'
        self.script_path = os.path.join(self.test_dir, self.script_name)

        # Read the script content from fixture
        fixture_path = os.path.join(self.test_dir, 'fixtures', 'test_curl_503.sh')
        with open(fixture_path, 'r') as f:
            script_content = f.read()

        # Create the test script from the fixture
        with open(self.script_path, 'w') as f:
            f.write(script_content)

        # Make the script executable
        os.chmod(self.script_path, 0o755)

    def tearDown(self):
        # Clean up created files
        if os.path.exists(self.script_path):
            os.remove(self.script_path)

        fake_llm_path = os.path.join(self.test_dir, 'llm')
        if os.path.exists(fake_llm_path):
            os.remove(fake_llm_path)

    def test_big_hammer_handles_503_error(self):
        # Path to big-hammer
        big_hammer_path = os.path.join(self.project_root, 'big-hammer')

        # Create a fake `llm` that outputs a fixed version that succeeds
        fake_llm_path = os.path.join(self.test_dir, 'llm')
        with open(fake_llm_path, 'w') as f:
            f.write("#!/bin/sh\n")
            # The "fixed" script just returns success
            f.write("echo '#!/bin/bash\necho \"Fixed: Skipping the failing curl call\"\nexit 0'\n")

        subprocess.run(['chmod', '+x', fake_llm_path], check=True)

        # Add the tests directory to the PATH so our fake llm is found
        env = os.environ.copy()
        env['PATH'] = self.test_dir + os.pathsep + env['PATH']

        # Run big-hammer with the failing script
        command_to_run = [big_hammer_path, 'bash', self.script_path]

        result = subprocess.run(command_to_run, capture_output=True, text=True, env=env, cwd=self.project_root)

        # Assertions
        self.assertIn("LLM suggested a fix", result.stdout,
                     f"Expected LLM fix message in stdout.\nStdout: {result.stdout}\nStderr: {result.stderr}")
        self.assertIn("Fix execution finished", result.stdout,
                     f"Expected fix execution to complete.\nStdout: {result.stdout}\nStderr: {result.stderr}")

if __name__ == '__main__':
    unittest.main()
