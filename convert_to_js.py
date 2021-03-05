import sys, subprocess

python_bin = sys.executable

def execute_shell(cmd):
    subprocess.run(cmd, shell=True, check=True)

# install transcrypt
execute_shell(f'{python_bin} -m pip install transcrypt')
# convert to js
execute_shell(f'{python_bin} -m transcrypt -mnv manimlib/__init__.py')
