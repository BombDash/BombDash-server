#!/usr/bin/env python3
# Copyright (c) 2020 BombDash

import sys
import os
import distutils.dir_util


def run(cmd, capture_stdout=False, show=True):
    if show:
        print(f'\033[01;33m$ {cmd}\033[00m')  # ]]
    if capture_stdout:
        return os.popen(cmd).read()
    os.system(cmd)


def build(build_type):
    run(f'mkdir -p build')
    os.chdir('build')
    if not os.path.exists('ballistica'):
        run('git clone "https://github.com/efroemling/ballistica"')
    else:
        run('cd ballistica && git pull')
    run(f'cd ballistica && make prefab-server-{build_type}-build')
    run(f'rm -rf {build_type}')
    run(f'cp -r ballistica/build/prefab/linux-server/{build_type}/ .')
    run(f'cp -r ../src/* {build_type}/dist/ba_data/')
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
