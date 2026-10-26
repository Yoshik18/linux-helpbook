#!/usr/bin/env python3
"""Run only selected, reviewed documentation examples in a temporary lab.

Requires Linux, Bash 4+, Python 3 and GNU coreutils. No sudo or cloud access.
Never use this harness to run arbitrary fenced examples from an untrusted repo.
"""
from pathlib import Path
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = (ROOT / 'shell-scripting/scripting.md').read_text()

def block_after(text, heading):
    section = text.split(heading, 1)[1]
    match = re.search(r'```bash\n(.*?)```', section, re.S)
    if match is None:
        raise ValueError(f'No Bash block found after {heading}')
    return match.group(1)

class Examples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='linux-helpbook-')
        self.addCleanup(self.temp.cleanup)
        self.env = dict(os.environ, TMPDIR=self.temp.name)

    def bash(self, code):
        return subprocess.run(['bash', '--noprofile', '--norc', '-c', code],
                              cwd=self.temp.name, env=self.env, text=True,
                              capture_output=True, timeout=15)

    def test_exit_trap_preserves_failure(self):
        code = block_after(GUIDE, '### Trap for Cleanup')
        result = self.bash(code + '\nexit 7\n')
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_counter_with_errexit(self):
        code = block_after(GUIDE, '### Loops')
        result = self.bash('set -e\n' + code)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Counter: 9', result.stdout)

    def test_local_scope(self):
        code = block_after(GUIDE, '### Variable Declaration')
        result = self.bash(code + '\nstatus=outside; show_status; printf "%s\\n" "$status"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'inside\noutside\n')

    def test_retry_keeps_arguments(self):
        code = block_after(GUIDE, '### Retry Mechanism')
        result = self.bash(code + '\nshow() { printf "%s:<%s>\\n" "$#" "$1"; }; retry 1 show "two words"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '1:<two words>\n')

    def test_retry_failure_and_invalid_input(self):
        code = block_after(GUIDE, '### Retry Mechanism')
        for suffix, expected in [('retry 1 false', 1), ('retry 0 true', 2),
                                 ('retry', 2)]:
            with self.subTest(suffix=suffix):
                result = self.bash('set -u\n' + code + '\n' + suffix)
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_warning_is_logged_and_sent_to_stderr(self):
        code = block_after(GUIDE, '### Logging Framework')
        result = self.bash('LOG_FILE=lab.log\n' + code + '\nlog WARN "test message"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertIn('WARN: test message', result.stderr)
        self.assertIn('WARN: test message', (Path(self.temp.name) / 'lab.log').read_text())

    def test_configuration_keeps_quotes_and_last_line(self):
        (Path(self.temp.name) / 'config').write_text(' # comment\n  \n host = localhost\nquoted = "two words"\nlast=value')
        code = block_after(GUIDE, '### Configuration File Parser')
        result = self.bash(code + '\nparse_config config; printf "%s|%s|%s\\n" "${config[host]}" "${config[quoted]}" "${config[last]}"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'localhost|"two words"|value\n')

    def test_getopts_missing_argument(self):
        code = block_after(GUIDE, '### Getopts Example')
        result = self.bash('set -- -f\n' + code)
        self.assertEqual(result.returncode, 1)
        self.assertIn('needs an argument', result.stderr)

    def test_directory_permissions_lab(self):
        if os.geteuid() == 0:
            self.skipTest('root can bypass directory mode checks')
        text = (ROOT / 'fundamentals/permissions.md').read_text()
        result = self.bash(block_after(text, '## Try it in a private lab'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Permission denied', result.stderr)
        self.assertEqual(result.stdout.count('hello'), 2)

    def test_disk_space_lab(self):
        text = (ROOT / 'troubleshooting/disk-space.md').read_text()
        result = self.bash(block_after(text, '## Try it yourself'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('.cache', result.stdout)
        blobs = list(Path(self.temp.name).rglob('sample.bin'))
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].stat().st_size, 1024 * 1024)

    def test_practice_pipeline_exit_statuses(self):
        text = (ROOT / 'fundamentals/13-practice-labs.md').read_text()
        result = self.bash(block_after(text, '## 1.'))
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ['Match status: 0', 'No-match status: 1',
                         'Read-error status: 2', 'Pipeline without pipefail: 0',
                         'Pipeline with pipefail: 2']:
            self.assertIn(expected, result.stdout)

    def test_practice_deleted_open_file(self):
        text = (ROOT / 'fundamentals/13-practice-labs.md').read_text()
        match = re.search(r'```python\n(.*?)```', text, re.S)
        self.assertIsNotNone(match)
        assert match is not None
        result = subprocess.run([sys.executable, '-'], input=match.group(1),
                                cwd=self.temp.name, env=self.env, text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ['Name exists: False', 'Link count: 0',
                         'Logical bytes: 1048576', "Still readable: b'xxxx'",
                         '(deleted)']:
            self.assertIn(expected, result.stdout)

    def test_practice_http_error_statuses(self):
        if shutil.which('curl') is None:
            self.skipTest('curl is not installed')
        text = (ROOT / 'fundamentals/13-practice-labs.md').read_text()
        section = text.split('## 3.', 1)[1]
        blocks = re.findall(r'```bash\n(.*?)```', section, re.S)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        start = blocks[0].replace('8765', str(port))
        start = start.replace('python3 -m http.server', 'exec python3 -m http.server')
        server = subprocess.Popen(['bash', '--noprofile', '--norc', '-c', start],
                                  cwd=self.temp.name, env=self.env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(30):
                self.assertIsNone(server.poll(), 'lab server exited before readiness')
                probe = subprocess.run(['curl', '--silent', '--fail', '--max-time', '1',
                                        f'http://127.0.0.1:{port}/'],
                                       capture_output=True, text=True)
                if probe.returncode == 0:
                    break
                time.sleep(0.1)
            else:
                self.fail('lab server did not become ready')
            self.assertEqual(probe.stdout, 'service is reachable\n')
            result = self.bash('set +e\n' + blocks[1].replace('8765', str(port)))
            self.assertEqual(result.returncode, 0, result.stderr)
            for expected in ['HTTP 404', 'curl status without --fail: 0',
                             'curl status with --fail: 22', 'service is reachable']:
                self.assertIn(expected, result.stdout)
        finally:
            server.terminate()
            server.wait(timeout=5)

if __name__ == '__main__':
    unittest.main(verbosity=2)
