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
        return {"max_cpu_time": 300,
                  "max_real_time": 1000,
                  "max_memory": 300 * 1024 * 1024,
                  "max_stack": 80 * 1024 * 1024,
                  "max_process_number": 1,
                  "max_output_size": 1024 * 1024,
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
        result = _judger.run(**config)
        print(result)
        self.assertEqual(result["result"], _judger.RESULT_SUCCESS)
        output = "2\n3\n4\n5\n6\ntest\ntest 2\n"
        self.assertEqual(output, self.get_file_contents(config["output_path"]))
    
    """
    def test_tle(self):
        config = self.get_config()
        self.populate_args(config, "tle.py")
        config["input_path"] = self.make_input("judger_test")
        config["output_path"] = config["error_path"] = self.output_path()
        result = _judger.run(**config)
        self.assertEqual(result["result"], _judger.RESULT_SUCCESS)
        output = "2\n3\n4\n5\n6\ntest\ntest 2\n"
        self.assertEqual(output, self.get_file_contents(config["output_path"]))
    """