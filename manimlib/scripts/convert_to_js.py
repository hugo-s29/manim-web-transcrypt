import sys, subprocess, os
import argparse
from fill_files_data import fill_files_data

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "manimlib"))

python_bin = sys.executable
transcrypt = f"{python_bin} -m transcrypt"

def execute_shell(cmd):
    subprocess.run(cmd, shell=True, check=True)

def install_transcrypt():
    execute_shell(f'{python_bin} -m pip install transcrypt')

def compile_manimlib_to_js():
    compile_file_to_js('manimlib/__init__.py')

def compile_file_to_js(file):
    execute_shell(f'{transcrypt} -mnv {file}')

try:
    parser = argparse.ArgumentParser(description="Convert manim to JavaScript")
    parser.add_argument("file", help="path to file holding the python code for the scene")
    parser.add_argument('-c', '--compile-manimlib', help="Compile manimlib to JavaScript (default: false)", nargs='?', default=False)
    parser.add_argument('-i', '--install-transcrypt', help="Install transcrypt automatically (default: false)", nargs='?', default=False)

    args = parser.parse_args()
except argparse.ArgumentError as err:
    print(str(err))
    sys.exit(2)

if args.install_transcrypt == None or args.install_transcrypt:
    install_transcrypt()

if args.compile_manimlib == None or args.compile_manimlib:
    fill_files_data()
    compile_manimlib_to_js()

compile_file_to_js(args.file)
