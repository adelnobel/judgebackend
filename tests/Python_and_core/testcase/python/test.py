# coding=utf-8
from __future__ import print_function
import timeit
import sys
import signal
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
        return {"max_cpu_time": 100,
                  "max_real_time": 999, # will be one second, ceils to 1000
                  "max_memory": 300 * 1024 * 1024,
                  "max_stack": 100 * 1024 * 1024,
                  "max_process_number": 200, # -1 for unlimited, setting this to a low number will cause execve to fail with Resource temporarily unavailable error. This should be fine to be -1 as seccomp should fight it
                  "max_output_size": 10 * 1024,
                  "exe_path": "/usr/bin/python3",
                  "input_path": "/dev/null",
                  "output_path": "/dev/null",
                  "error_path": "/dev/null",
                  "args": [],
                  "env": ["env=judger_test", "test=judger"],
                  "log_path": "judger_test.log",
                  "seccomp_rule_name": "general",
                  "uid": 0,
                  "gid": 65534} 
        return config
    
    def populate_args(self, config, src_name):
        path = self.get_file_absolute_path("../../test_src/python/" + src_name)
        content = self.get_file_contents(path)
        config["args"] = ["-c", content]

    def test_normal(self):
        config = self.get_config()
        self.populate_args(config, "ok.py")
        config["input_path"] = self.make_input("judger_test")
        config["output_path"] = config["error_path"] = self.output_path()
        config["seccomp_rule_name"] = "python"
        result = _judger.run(**config)
        print(result)
        print(self.get_file_contents(config["output_path"]))
        self.assertEqual(result["result"], _judger.RESULT_SUCCESS)
        output = "2\n3\n4\n5\n6\ntest\ntest 2\n"
        self.assertEqual(output, self.get_file_contents(config["output_path"]))
    

    def test_tle_cpu(self):
        config = self.get_config()
        self.populate_args(config, "tle_cpu.py")
        config["input_path"] = self.make_input("judger_test")
        config["output_path"] = config["error_path"] = self.output_path()
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_CPU_TIME_LIMIT_EXCEEDED)

    def test_tle_time(self):
        config = self.get_config()
        self.populate_args(config, "tle_time.py")
        config["input_path"] = self.make_input("judger_test")
        config["output_path"] = config["error_path"] = self.output_path()
        result = _judger.run(**config)
        print(self.get_file_contents(config["output_path"]))
        self.assertEqual(result["result"], _judger.RESULT_REAL_TIME_LIMIT_EXCEEDED)


