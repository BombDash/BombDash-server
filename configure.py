#!/usr/bin/env python3
# Copyright (c) 2020 BombDash

import sys
import os
import subprocess


def run(cmd, capture_stdout=False, show=True, doraise=True):
    if show:
        print(f'\033[01;33m$ {cmd}\033[00m')  # ]]
    process = subprocess.Popen(
        ['sh', '-c', cmd],
        # stdout=subprocess.PIPE if capture_stdout else subprocess.STDOUT
        )
    errno = process.wait()
    if errno and doraise:
        raise RuntimeError(f'Process `{cmd}` exited with code {errno}')
    return False if errno else process.stdout.read() if capture_stdout else True


def build(build_type, only_copy=False):
    run(f'mkdir -p build')
    os.chdir('build')
    if only_copy:
        run(f'cp -rf ../src/* {build_type}/dist/ba_data/') # TODO: use rsync instead
    else:
        if not os.path.exists('ballistica'):
            run('git clone "https://github.com/efroemling/ballistica"')
        else:
            run('cd ballistica && git pull')
        run(f'cp -rf ../src/* ballistica/assets/src/ba_data/')
        run('echo \'{"license_line_checks": false}\' > ballistica/config/localconfig.json')
        run('ballistica/tools/pcommand install_pip_reqs')
        run(f'cd ballistica && make update')
        run(f'cd ballistica && make prefab-server-{build_type}-build')
        run(f'rm -rf {build_type}')
        run(f'cp -r ballistica/build/prefab/full/linux_x86_64_server/{build_type}/ .')
    os.chdir('..')


usage_text = (f'Usage:\n'
              f'    {sys.argv[0]} <target>\n'
              f'\n'
              f'target may be one of ["build-debug", "build-release", "run-debug"]')

if len(sys.argv) < 2:
    print(usage_text)
    exit(0)

if sys.argv[1] == 'build-debug':
    build('debug')
elif sys.argv[1] == 'build-release':
    build('release')
elif sys.argv[1] == 'run-debug':
    run("cd build/debug && ./ballisticacore_server")
elif sys.argv[1] == 'copy-files-debug':
    build('debug', only_copy=True)
elif sys.argv[1] == 'copy-files-release':
    print('Oops.. only copy for release is very bad (python will use compiled .pyc files instead)')
elif sys.argv[1] == 'mypy':
    run('python3.7 -m mypy --config-file config/mypy.ini src/python/')
else:
    print('What?')
    exit(-1)
