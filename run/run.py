# -*- coding: utf-8 -*-
# @Time    : 2019-03-19 23:05
# @Author  : Aimee
# @File    : run.py

import time
import unittest

from BeautifulReport import BeautifulReport

from testcase import get_upper_text_test

report_path = '/home/aimee/PycharmProjects/grpc_unittest_demo/report'
now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromModule(get_upper_text_test))
    BeautifulReport(suite).report(filename=now_time + '_result', description='UpperCase', log_path=report_path)
