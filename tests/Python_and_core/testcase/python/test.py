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

    def setUp(self):
        print("Running", self._testMethodName)
        self.workspace = self.init_workspace("integration")
        self.startTime = timeit.default_timer()

    def tearDown(self):
        print("Time: ", timeit.default_timer() - self.startTime)

    def get_config(self):
        return {"max_cpu_time": 400,
                "max_real_time": 999,  # will be one second, ceils to 1000
                "max_memory": 600 * 1024 * 1024,
                "max_stack": 300 * 1024 * 1024,
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
                "chroot_path": self.CHROOT_DIR,
                "uid": 65534,
                "gid": 65534}
        return config

    def populate_args(self, config, src_name):
        path = self.get_file_absolute_path("../../test_src/python/" + src_name)
        content = self.get_file_contents(path)
        config["args"] = ["-c", content]

    def helper(self, test_file, expected_result, expected_signal,
               input_val=None, expected_output=None, override_config=None):
        config = self.get_config()
        if override_config is not None:
            config.update(override_config)
        self.populate_args(config, test_file)
        absolute_output_path = self.output_path()
        if input_val is not None:
            config["input_path"] = self.get_path_relative_to_chroot(
                self.make_input(input_val))
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(
            absolute_output_path)
        result = _judger.run(**config)
        print(result)
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
            input_val=None, expected_output=None)

    def test_mkdir(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="mkdir.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val=None, expected_output=None)

    def test_system(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="system.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val=None, expected_output=None)

    def test_subprocess(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="subprocess.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val=None, expected_output=None, override_config=None)

    def test_opencreate(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="opencreate.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val=None, expected_output=None, override_config=None)

    def test_openwrite(self):
        # signal 31 -> bad system call (check logs)
        self.helper(
            test_file="opencreate.py",
            expected_result=_judger.RESULT_RUNTIME_ERROR, expected_signal=31,
            input_val=None, expected_output=None, override_config=None)

    def test_count_writable(self):
        """
            This test is a safety check to make sure there is no writable directories 
            or files, if this test fails then you want to make sure permissions are set 
            correctly on all the files in the chroot folder
        """
        root_path = os.path.join(
            self.CHROOT_DIR, "nowthispathdoesntexist")
        shutil.rmtree(root_path, ignore_errors=True)

        # First lets make sure there is 0 writable files and directories
        self.helper(
            test_file="count_writable.py",
            expected_result=_judger.RESULT_SUCCESS, expected_signal=0,
            input_val="1", expected_output="0\n0\n")

        # Now lets create some writable file and make sure it gets read
        try:
            original_umask = os.umask(0)
            file_dir = os.path.join(root_path, "dummy1", "dummy2")
            os.makedirs(file_dir, 0o777)
            file_path = os.path.join(file_dir, "dummy.txt")
            open(file_path, "x").close()
            os.chmod(file_path, 0o766)
        finally:
            os.umask(original_umask)

        self.helper(
            test_file="count_writable.py",
            expected_result=_judger.RESULT_SUCCESS, expected_signal=0,
            input_val="5", expected_output="3\n1\n")

        # delete the dummy path
        shutil.rmtree(root_path, ignore_errors=True)
