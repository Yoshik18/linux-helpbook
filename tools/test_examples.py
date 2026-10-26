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
        self.initial_tmp_entries = set(Path(self.temp.name).iterdir())

    def bash(self, code, *args):
        command = ['bash', '--noprofile', '--norc', '-c', code]
        if args:
            command.extend(['--', *args])
        return subprocess.run(command, cwd=self.temp.name, env=self.env, text=True,
                              capture_output=True, timeout=15)

    def test_complete_line_count_script(self):
        code = block_after(GUIDE, '## Small complete example')
        script = Path(self.temp.name) / 'line-count.sh'
        script.write_text(code)
        sample = Path(self.temp.name) / 'sample.txt'
        sample.write_text('one\ntwo\nthree\n')
        result = subprocess.run(['bash', str(script), str(sample)], cwd=self.temp.name,
                                env=self.env, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'{sample}: 3 lines', result.stdout)

    def test_forward_arguments_with_spaces(self):
        code = block_after(GUIDE, '## Arguments are already separate values')
        result = self.bash(code + '\n' + "printf 'count=%s\\n' \"$#\"", 'two words')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Path argument: <two words>', result.stdout)
        self.assertIn('count=1', result.stdout)

    def test_cleanup_preserves_exit_status(self):
        code = block_after(GUIDE, '## Temporary files and cleanup')
        result = self.bash(code + '\nexit 7\n')
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(set(Path(self.temp.name).iterdir()), self.initial_tmp_entries)

    def test_directory_permissions_lab(self):
        if os.geteuid() == 0:
            self.skipTest('root can bypass directory mode checks')
        text = (ROOT / 'fundamentals/permissions.md').read_text()
        result = self.bash(block_after(text, '## Change one practice file'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('600', result.stdout)
        self.assertIn('744', result.stdout)
        lab_script = Path(self.env['LINUX_LAB']) / 'bin/hello.sh'
        self.assertEqual(lab_script.stat().st_mode & 0o777, 0o744)

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
        result = self.bash(block_after(text, '## Lab 1:'))
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ['without pipefail: 0', 'with pipefail: 2']:
            self.assertIn(expected, result.stdout)

    def test_file_copy_and_rename(self):
        text = (ROOT / 'fundamentals/02-filesystem-and-paths.md').read_text()
        result = self.bash(block_after(text, '## Create, copy, move, remove'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'work/reports/tasks.txt').read_text(),
                         (lab / 'notes/todo.txt').read_text())
        self.assertFalse((lab / 'work/tasks.txt').exists())

    def test_link_identity(self):
        text = (ROOT / 'fundamentals/02-filesystem-and-paths.md').read_text()
        result = self.bash('mkdir "$LINUX_LAB/work"\n' + block_after(text, '## Links name data in different ways'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'notes/todo.txt').stat().st_ino,
                         (lab / 'work/todo-hardlink').stat().st_ino)
        self.assertEqual((lab / 'work/todo-shortcut').read_text(),
                         (lab / 'notes/todo.txt').read_text())

    def test_archive_round_trip(self):
        text = (ROOT / 'fundamentals/02-filesystem-and-paths.md').read_text()
        result = self.bash(block_after(text, '## Archive a directory and compare a restore'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'restored/notes/file with spaces.txt').read_text(),
                         (lab / 'notes/file with spaces.txt').read_text())

    def test_fixture_error_counts(self):
        text = (ROOT / 'fundamentals/03-shell-and-text.md').read_text()
        result = self.bash(block_after(text, '## Search and count repeated lines'))
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
        result = self.bash(block_after(text, '## Change only the permission you intend'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('hello from the lab'), 2)

    def test_umask_fixture(self):
        text = (ROOT / 'fundamentals/04-users-and-access.md').read_text()
        result = self.bash(block_after(text, '## Umask limits new permissions'))
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = Path(self.env['LINUX_LAB'])
        self.assertEqual((lab / 'notes/new-private.txt').stat().st_mode & 0o777, 0o600)
        self.assertEqual((lab / 'private-dir').stat().st_mode & 0o777, 0o700)

    def test_terminate_only_lab_child(self):
        text = (ROOT / 'fundamentals/05-processes-and-signals.md').read_text()
        result = self.bash(block_after(text, '## Signals and safe shutdown'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('child status: 143', result.stdout)

    def test_sparse_file_fixture(self):
        text = (ROOT / 'fundamentals/07-storage-and-filesystems.md').read_text()
        result = self.bash(block_after(text, '## Logical size differs from allocated space'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((Path(self.env['LINUX_LAB']) / 'data/sparse.bin').stat().st_size,
                         1024 * 1024)

    def test_practice_deleted_open_file(self):
        text = (ROOT / 'fundamentals/07-storage-and-filesystems.md').read_text()
        result = self.bash(block_after(text, '## A deleted name can still consume space'))
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ['still readable', '(deleted)']:
            self.assertIn(expected, result.stdout)

    def test_practice_http_error_statuses(self):
        if shutil.which('curl') is None:
            self.skipTest('curl is not installed')
        text = (ROOT / 'fundamentals/10-networking.md').read_text()
        section = text.split('## 4. Test connection and application response separately', 1)[1]
        blocks = re.findall(r'```bash\n(.*?)```', section, re.S)
        self.assertGreaterEqual(len(blocks), 2, 'expected local server and client command blocks')
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
            for expected in ['HTTP 404', 'learn files', 'read logs']:
                self.assertIn(expected, result.stdout)
        finally:
            server.terminate()
            server.wait(timeout=5)

if __name__ == '__main__':
    unittest.main(verbosity=2)
