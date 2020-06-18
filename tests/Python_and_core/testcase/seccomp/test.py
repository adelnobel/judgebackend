# coding=utf-8
from __future__ import print_function
import timeit
import _judger
import signal
import shutil
import os

from .. import base


class SeccompTest(base.BaseTestCase):
    def setUp(self):
        print("Running", self._testMethodName)
        self.workspace = self.init_workspace("integration")
        self.startTime = timeit.default_timer()

    def tearDown(self):
        print("Time: ", timeit.default_timer() - self.startTime)

    def _compile_c(self, src_name, extra_flags=None):
        return super(SeccompTest, self)._compile_c("../../test_src/seccomp/" + src_name, extra_flags)

    def test_fork(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("fork.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)

        # with general seccomp
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

        # with c_cpp seccomp
        config["seccomp_rule_name"] = "c_cpp"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

    def test_execve(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("execve.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)

        # with general seccomp
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

        # with c_cpp seccomp
        config["seccomp_rule_name"] = "c_cpp"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

    def test_write_file_using_open(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("write_file_open.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)
        path = os.path.join(self.workspace, "file1.txt")
        config["args"] = [path, "w"]

        # with general seccomp
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

        # with c_cpp seccomp
        config["seccomp_rule_name"] = "c_cpp"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

    def test_read_write_file_using_open(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("write_file_open.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)
        path = os.path.join(self.workspace, "file2.txt")
        config["args"] = [path, "w+"]


        # with general seccomp
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

        # with c_cpp seccomp
        config["seccomp_rule_name"] = "c_cpp"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

    def test_write_file_using_openat(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("write_file_openat.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)
        path = os.path.join(self.workspace, "file3.txt")
        config["args"] = [path, "w"]

        # with general seccomp
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

        # with c_cpp seccomp
        config["seccomp_rule_name"] = "c_cpp"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

    def test_read_write_file_using_openat(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("write_file_openat.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)
        path = os.path.join(self.workspace, "file4.txt")
        config["args"] = [path, "w+"]

        # with general seccomp
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

        # with c_cpp seccomp
        config["seccomp_rule_name"] = "c_cpp"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)

    def test_sysinfo(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("sysinfo.c")
        result = _judger.run(**config)

        self.assertEqual(result["result"], _judger.RESULT_SUCCESS)

    def test_exceveat(self):
        config = self.base_config
        config["exe_path"] = self._compile_c("execveat.c")
        output_path = self.output_path()
        config["output_path"] = config["error_path"] = self.get_path_relative_to_chroot(output_path)
        
        # with general seccomp 
        config["seccomp_rule_name"] = "general"
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_RUNTIME_ERROR)
        self.assertEqual(result["signal"], self.BAD_SYSTEM_CALL)
