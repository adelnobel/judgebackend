# coding=utf-8
from __future__ import print_function
import os
import random
import shutil
import copy
from unittest import TestCase


class RunResult(object):
    cpu_time_limited = 1
    real_time_limit_exceeded = 2
    memory_limit_exceeded = 3
    runtime_error = 4
    system_error = 5


class BaseTestCase(TestCase):
    BAD_SYSTEM_CALL = 31
    CHROOT_DIR = "/home/adelaly/Desktop/python-jail"

    def init_workspace(self, language):
        base_workspace = os.path.join(self.CHROOT_DIR, "tmp")
        workspace = os.path.join(base_workspace, language)
        shutil.rmtree(workspace, ignore_errors=True)
        os.makedirs(workspace)
        return workspace

    def tearDown(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def rand_str(self):
        return "".join([random.choice("123456789abcdefghijklmn") for _ in range(12)])

    def _compile_c(self, src_name, extra_flags=None):
        exe_path = os.path.join(self.workspace, src_name.split("/")[-1].split(".")[0])
        flags = " "
        if extra_flags:
            flags += " ".join(extra_flags)
        cmd = ("gcc {0} -g -O0 -static -o {1}" + flags).format(self.get_file_absolute_path(src_name), exe_path)
        if os.system(cmd):
            raise AssertionError("compile error, cmd: {0}".format(cmd))
        return self.get_path_relative_to_chroot(exe_path)

    def _compile_cpp(self, src_name):
        exe_path = os.path.join(self.workspace, src_name.split("/")[-1].split(".")[0])
        cmd = "g++ {0} -g -O0 -o {1}".format(self.get_file_absolute_path(src_name), exe_path)
        if os.system(cmd):
            raise AssertionError("compile error, cmd: {0}".format(cmd))
        return self.get_path_relative_to_chroot(exe_path)
    
    def get_file_absolute_path(self, src_name):
        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, src_name)

    def get_path_relative_to_chroot(self, path):
        return "/" + os.path.relpath(path, self.CHROOT_DIR)

    def make_input(self, content):
        path = os.path.join(self.workspace, self.rand_str())
        with open(path, "w") as f:
            f.write(content)
        return path

    def output_path(self):
        return os.path.join(self.workspace, self.rand_str())

    def get_file_contents(self, path):
        with open(path, "r") as f:
            return f.read()

    @property
    def base_config(self):
        config = {"max_cpu_time": 1000,
                  "max_real_time": 3000,
                  "max_memory": 400 * 1024 * 1024,
                  "max_stack": 32 * 1024 * 1024,
                  "max_process_number": 10,
                  "max_output_size": 1024 * 1024,
                  "exe_path": "/bin/python3",
                  "input_path": "/dev/null",
                  "output_path": "/dev/null",
                  "error_path": "/dev/null",
                  "args": ['-c', '""'],
                  "env": ["env=judger_test", "test=judger"],
                  "log_path": "judger_test.log",
                  "seccomp_rule_name": None,
                  "chroot_path": self.CHROOT_DIR,
                  "uid": 0,
                  "gid": 0}
        return config
