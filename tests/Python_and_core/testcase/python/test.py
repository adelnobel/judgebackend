# coding=utf-8
from __future__ import print_function
import timeit
import sys
import signal
import shutil
import os
import resource
import _judger

from .. import base


class PythonTest(base.BaseTestCase):
    PYTHON_CHROOT_FOLDER = "/home/adelaly/Desktop/python-jail"

    def init_workspace(self, language):
        base_workspace = os.path.join(self.PYTHON_CHROOT_FOLDER, "tmp")
        workspace = os.path.join(base_workspace, language)
        shutil.rmtree(workspace, ignore_errors=True)
        os.makedirs(workspace)
        return workspace

    def setUp(self):
        print("Running", self._testMethodName)
        self.workspace = self.init_workspace("integration")
        self.startTime = timeit.default_timer()

    def tearDown(self):
        print("Time: ", timeit.default_timer() - self.startTime)

    def get_config(self):
        return {"max_cpu_time": 100,
                "max_real_time": 999,  # will be one second, ceils to 1000
                "max_memory": 300 * 1024 * 1024,
                "max_stack": 100 * 1024 * 1024,
                "max_process_number": 200,  # -1 for unlimited, setting this to a low number will cause execve to fail with Resource temporarily unavailable error. This should be fine to be -1 as seccomp should fight it
                "max_output_size": 1024 * 1024,
                "exe_path": "/bin/python3.8",
                "input_path": "/dev/null",
                "output_path": "/dev/null",
                "error_path": "/dev/null",
                "args": [],
                # "PYTHONHOME=/" must be set
                "env": ["PYTHONHOME=/", "test=judger"],
                "log_path": "/log/judger_test.log",
                "seccomp_rule_name": "python",
                "chroot_path": self.PYTHON_CHROOT_FOLDER,
                "uid": 65534,
                "gid": 65534}
        return config

    def populate_args(self, config, src_name):
        path = self.get_file_absolute_path("../../test_src/python/" + src_name)
        content = self.get_file_contents(path)
        config["args"] = ["-c", content]

    # Convert absolute path to path relative to chroot jail so we can feed into judger

    def convert_to_relative_to_chroot_path(self, path):
        return path.replace(self.PYTHON_CHROOT_FOLDER, "")

    def helper(self, test_file, expected_result, expected_signal,
               input_val=None, expected_output=None, override_config=None):
        config = self.get_config()
        if override_config is not None:
            config.update(override_config)
        self.populate_args(config, test_file)
        absolute_output_path = self.output_path()
        if input_val is not None:
            config["input_path"] = self.convert_to_relative_to_chroot_path(
                self.make_input(input_val))
        config["output_path"] = config["error_path"] = self.convert_to_relative_to_chroot_path(
            absolute_output_path)
        result = _judger.run(**config)
        print(self.get_file_contents(absolute_output_path))
        self.assertEqual(result["result"], expected_result)
        self.assertEqual(result["signal"], expected_signal)
        if expected_output is not None:
            self.assertEqual(
                expected_output, self.get_file_contents(absolute_output_path))

    def test_normal(self):
        # signal 0 -> ok
        self.helper(
            test_file="ok.py", expected_result=_judger.RESULT_SUCCESS,
            expected_signal=0, input_val="wtf",
            expected_output="2\n3\n4\n5\n6\ntest\ntest 2\n")

    def test_arabic(self):
        # signal 0 -> ok
        self.helper(
            test_file="arabic.py", expected_result=_judger.RESULT_SUCCESS,
            expected_signal=0, input_val="3\nصبح",
            expected_output="احلى مسا على فخادك\nصبح\nصبح\nصبح\n")
    
    def test_ok_modules(self):
        # signal 0 -> ok
        self.helper(
            test_file="ok_modules.py", expected_result=_judger.RESULT_SUCCESS,
            expected_signal=0, input_val="3",
            expected_output="9.0\n")

    def test_tle_cpu(self):
        # signal 9 -> killed
        self.helper(
            test_file="tle_cpu.py",
            expected_result=_judger.RESULT_CPU_TIME_LIMIT_EXCEEDED,
            expected_signal=9, input_val=None, expected_output=None)

    def test_sleep(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="sleep.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val="wtf", expected_output=None)

    def test_mkdir(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="mkdir.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val="wtf", expected_output=None)

    def test_system(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="system.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val="wtf", expected_output=None)