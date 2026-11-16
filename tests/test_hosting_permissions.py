import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_hosting import build


class HostingPermissionsTests(unittest.TestCase):
    def test_restrictive_umask_keeps_all_exported_files_readable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            previous = os.umask(0o077)
            try:
                files = build(output=output)
            finally:
                os.umask(previous)
            self.assertEqual(output.stat().st_mode & 0o777, 0o755)
            for path in output.rglob('*'):
                self.assertEqual(path.stat().st_mode & 0o777,
                                 0o755 if path.is_dir() else 0o644, str(path))
                if path.is_file():
                    self.assertEqual(path.read_bytes(), files[path.relative_to(output).as_posix()])
            archive = Path(temporary) / 'release.zip'
            with zipfile.ZipFile(archive, 'w') as zipped:
                for name in files:
                    zipped.write(output / name, name)
            with zipfile.ZipFile(archive) as zipped:
                for item in zipped.infolist():
                    self.assertEqual((item.external_attr >> 16) & 0o777, 0o644)
                    self.assertEqual(zipped.read(item.filename), files[item.filename])


if __name__ == '__main__':
    unittest.main()
