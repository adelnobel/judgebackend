#! /bin/bash
set -ex
dir=$PWD
python3 -V
gcc -v
g++ -v

cd $dir
cd "src"
printf $PWD
bazel build :judger
cd ../tests && python3 test.py

