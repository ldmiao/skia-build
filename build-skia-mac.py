#!/usr/bin/env python3

import sys
import os
import argparse
import subprocess

def run(command):
    try:
        result = subprocess.run(command, stderr=sys.stderr, stdout=sys.stdout)
        if result.returncode != 0:
            print('"{}" exited with {}'.format(command, result.returncode))
            exit(1)
    except Exception as e:
        print('Error when running "{}":\n  {}'.format(command, str(e)))
        exit(1)


parser = argparse.ArgumentParser()
parser.add_argument('--branch', help='Specify which branch to build', default='master')
args = parser.parse_args()

# depot_tools
if not os.path.isdir('depot_tools'):
    run(['git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'])

# skia source
if not os.path.isdir('skia'):
    run(['git', 'clone', 'https://skia.googlesource.com/skia'])
    run(['./skia/tools/install_dependencies.sh'])
run(['git', '-C', 'skia', 'checkout', args.branch])
run(['git', '-C', 'skia', 'pull'])
run(['python', 'skia/tools/git-sync-deps'])

run(['tar', '-czf', 'skia-all-darwin.tar.gz', 'skia', 'depot_tools'])

# build
shared_args = [
    'is_debug=false',
    'is_component_build=true',
    'is_official_build=true',
    'skia_enable_tools=false',
    'target_os="mac" target_cpu="x64"',
    'cc="clang" cxx="clang++"',
    'skia_use_lua=true',
    'skia_use_icu=false skia_use_sfntly=false skia_use_piex=true',
    'skia_use_system_expat=false',
    'skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false',
    'skia_use_system_libwebp=false skia_use_system_zlib=false',
    'skia_enable_gpu=true']
static_args = [
    'is_debug=false',
    'is_official_build=true',
    'skia_enable_tools=false',
    'target_os="mac" target_cpu="x64"',
    'cc="clang" cxx="clang++"',
    'skia_use_lua=true',
    'skia_use_icu=false skia_use_sfntly=false skia_use_piex=true',
    'skia_use_system_expat=false',
    'skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false',
    'skia_use_system_libwebp=false skia_use_system_zlib=false',
    'skia_enable_gpu=true']
run(['./skia/bin/gn', '--root=skia', 'gen', 'skia/out/darwin-x64-shared', '--args=' + ' '.join(shared_args)])
run(['./depot_tools/ninja', '-C', 'skia/out/darwin-x64-shared', 'skia'])
run(['./skia/bin/gn', '--root=skia', 'gen', 'skia/out/darwin-x64-static', '--args=' + ' '.join(static_args)])
run(['./depot_tools/ninja', '-C', 'skia/out/darwin-x64-static', 'skia'])

run(['cp', 'skia/out/darwin-x64-shared/libskia.so', 'libskia-darwin-x64.dylib'])
#run(['strip', '-s', 'libskia-darwin-x64.dylib'])
run(['cp', 'skia/out/darwin-x64-static/libskia.a', 'libskia-darwin-x64.a'])
run(['tar', '-czf', 'skia-headers-darwin.tar.gz', 'skia/include/'])
#run(['tar', '-czf', 'skia-all-darwin.tar.gz', 'skia', 'depot_tools'])

print("Finish")
