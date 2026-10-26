#!/usr/bin/env python3
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
subprocess.run(['git','config','--local','core.hooksPath','.githooks'],cwd=root,check=True)
(root/'.githooks/pre-commit').chmod(0o755)
print('Installed local pre-commit credential/source consistency gate.')
