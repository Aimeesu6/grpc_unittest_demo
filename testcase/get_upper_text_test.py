#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 3/18/19 1:50 PM 
# @Author : Aimee

import grpc
import unittest

from protobuf import data_pb2, data_pb2_grpc

_HOST = 'localhost'
_PORT = '8000'


class GetUpperTextTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = grpc.insecure_channel(_HOST + ':' + _PORT)
        cls.client = data_pb2_grpc.FormatDataStub(channel=cls.conn)

    def test_1_lower_letters(self):
        args = data_pb2.Data()
        args.text = 'Convert to uppercase successfully'
        response = self.client.DoFormat(args)
        print(response.text)
        self.assertEqual(response.text, 'CONVERT TO UPPERCASE SUCCESSFULLY')

    def test_2_data_null(self):
        args = data_pb2.Data()
        args.text = ''
        response = self.client.DoFormat(args)
        print(response.text)
        self.assertEqual(response.text, '')

    def test_3_data_Chinese(self):
        args = data_pb2.Data()
        args.text = '我是中文'
        response = self.client.DoFormat(args)
        print(response.text)
        self.assertEqual(response.text, '我是中文')

    def test_4_data_Spechars(self):
        args = data_pb2.Data()
        args.text = '><?$%&*|{]~'
        response = self.client.DoFormat(args)
        print(response.text)
        self.assertEqual(response.text, '><?$%&*|{]~')

    def test_5_data_combination(self):
        args = data_pb2.Data()
        args.text = 'A_a$%B_b&*_中文_|{ ]~'
        response = self.client.DoFormat(args)
        print(response.text)
        self.assertEqual(response.text, 'A_A$%B_B&*_中文_|{ ]~')

    @classmethod
    def tearDownClass(cls):
        print('\n'
              '***************************\n'
              '测试完成')
