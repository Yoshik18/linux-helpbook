#!/usr/bin/env python3
"""Run only selected, reviewed documentation examples in a temporary lab.

Requires Linux, Bash 4+, Python 3 and GNU coreutils. No sudo or cloud access.
Never use this harness to run arbitrary fenced examples from an untrusted repo.
"""
from pathlib import Path
import os
import re
import shlex
import shutil
import socket
import subprocess
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
        setup = shlex.quote(str(ROOT / 'fundamentals/labs/setup.sh'))
        result = self.bash(f'source {setup} >/dev/null && printf "%s" "$LINUX_LAB"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.env['LINUX_LAB'] = result.stdout

    def bash(self, code):
        return subprocess.run(['bash', '--noprofile', '--norc', '-c', code],
                              cwd=self.temp.name, env=self.env, text=True,
                              capture_output=True, timeout=15)

    def test_exit_trap_preserves_failure(self):
        code = block_after(GUIDE, '### Trap for Cleanup')
        before = set(Path(self.temp.name).iterdir())
        result = self.bash(code + '\nexit 7\n')
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(set(Path(self.temp.name).iterdir()), before)

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
        for expected in ['without pipefail: 0', 'with pipefail: 2']:
            self.assertIn(expected, result.stdout)

    def test_file_copy_and_rename(self):
        text = (ROOT / 'fundamentals/02-filesystem-and-paths.md').read_text()
        result = self.bash(block_after(text, '## Create, copy and rename'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'work/reports/tasks.txt').read_text(),
                         (lab / 'notes/todo.txt').read_text())
        self.assertFalse((lab / 'work/tasks.txt').exists())

    def test_link_identity(self):
        text = (ROOT / 'fundamentals/02-filesystem-and-paths.md').read_text()
        result = self.bash('mkdir "$LINUX_LAB/work"\n' + block_after(text, '## Inspect links'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'notes/todo.txt').stat().st_ino,
                         (lab / 'work/todo-hardlink').stat().st_ino)
        self.assertEqual((lab / 'work/todo-shortcut').read_text(),
                         (lab / 'notes/todo.txt').read_text())

    def test_archive_round_trip(self):
        text = (ROOT / 'fundamentals/02-filesystem-and-paths.md').read_text()
        result = self.bash(block_after(text, '## Create and inspect a backup archive'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'restored/notes/file with spaces.txt').read_text(),
                         (lab / 'notes/file with spaces.txt').read_text())

    def test_fixture_error_counts(self):
        text = (ROOT / 'fundamentals/03-shell-and-text.md').read_text()
        result = self.bash(block_after(text, '## Count repeated errors'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r'2 ERROR api timeout')
        self.assertRegex(result.stdout, r'1 ERROR db refused')

    def test_fixture_field_filtering(self):
        text = (ROOT / 'fundamentals/03-shell-and-text.md').read_text()
        result = self.bash(block_after(text, '## Select fields'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('192.0.2.11 /orders 500', result.stdout)
        self.assertIn('192.0.2.12 /orders 500', result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith('165'))

    def test_lab_script_execute_permission(self):
        text = (ROOT / 'fundamentals/04-users-and-access.md').read_text()
        result = self.bash(block_after(text, '## Make one lab script executable'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('hello from the lab'), 2)

    def test_umask_fixture(self):
        text = (ROOT / 'fundamentals/04-users-and-access.md').read_text()
        result = self.bash(block_after(text, '## Observe umask'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'notes/new-private.txt').stat().st_mode & 0o777, 0o600)
        self.assertEqual((lab / 'private-dir').stat().st_mode & 0o777, 0o700)

    def test_terminate_only_lab_child(self):
        text = (ROOT / 'fundamentals/05-processes-and-signals.md').read_text()
        result = self.bash(block_after(text, '## Send SIGTERM'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('terminated child status: 143', result.stdout)

    def test_sparse_file_fixture(self):
        text = (ROOT / 'fundamentals/07-storage-and-filesystems.md').read_text()
        result = self.bash(block_after(text, '## See why apparent size'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((Path(self.env['LINUX_LAB']) / 'data/sparse.bin').stat().st_size,
                         1024 * 1024)

    def test_practice_deleted_open_file(self):
        text = (ROOT / 'fundamentals/13-practice-labs.md').read_text()
        result = self.bash(block_after(text, '## 2.'))
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ['still readable', '(deleted)']:
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
        setup = shlex.quote(str(ROOT / 'fundamentals/labs/setup.sh'))
        start = start.replace('source fundamentals/labs/setup.sh', f'source {setup}')
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
            self.assertIn('todo.txt', probe.stdout)
            result = self.bash('set +e\n' + blocks[1].replace('8765', str(port)))
            self.assertEqual(result.returncode, 0, result.stderr)
            for expected in ['HTTP 404', 'plain curl: 0',
                             'curl with fail: 22', 'learn files', 'read logs']:
                self.assertIn(expected, result.stdout)
        finally:
            server.terminate()
            server.wait(timeout=5)

if __name__ == '__main__':
    unittest.main(verbosity=2)
