#!/usr/bin/env python

'''
Tests for config_parser.

@author: jessedavis
'''

import nose
from nose.tools import *
import unittest

import simpleparse
from simpleparse.common import strings, numbers

# make this a bit better
import sys
sys.path.insert(0, '..')

import config_grammar
from config_loader import ConfigLoader

class test_config_parser(unittest.TestCase):

    parser = None
    loader = None

    @classmethod
    def setUpClass(self):
	self.parser = simpleparse.parser.Parser(config_grammar.config_minilang, 'root')
	self.loader = ConfigLoader()

    def setup(self):
	pass

    def teardown():
	self.loader.env_vars = {}

    @classmethod
    def tearDownAll(self):
	pass

    def test_variable(self):
	strings = [
            "bleh",
            "ENV.bleh",
            "ENV.bleh.bluh",
	]
	for string in strings:
	    self.parser.parse(string, processor=self.loader)
	    self.assertEqual(string, self.loader.value)

    def test_variable_source(self):
	strings = { "ENV.bleh": "ENV",
	            "ENVTOO.bleh.bluh": "ENVTOO",
	}	
	for string, env in strings.iteritems():
	    self.parser.parse(string, processor=self.loader)
	    self.assertEqual(env, self.loader.vars_section)

    @with_setup(setup, teardown)
    def test_eval_variables(self):
	var = 'a'	
	expressions = { '$var': 'a',
	                'bleh.$var': 'bleh.a',
	                '$var.$var': 'a.a',
			'ENV.$var.bleh': 'ENV.a.bleh',
	                'ENV.bleh.$var': 'ENV.bleh.a',
	              }

	self.loader.env_vars = { 'var': 'a' }

	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    @with_setup(setup, teardown)
    def test_eval_variable_error(self):
	var = 'a'
	expressions = { '$unknownvar': 'b', }

	self.loader.env_vars = { 'var': 'a' }

	for expression in expressions:
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(None, self.loader.value)

    def test_expression_if(self):
	expressions = [
	    "ENV.bleh.bleh|www"
	]
	for expression in expressions:
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(expression, self.loader.value)

    def test_expression_concat(self):
	expressions = [
	    "ENV.bleh.bleh+www"
	]
	for expression in expressions:
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(expression, self.loader.value)

    def test_expression_complex(self):
	expressions = [
	    "ENV.bleh.bleh|www|blank"
	]
	for expression in expressions:
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(expression, self.loader.value)

    @with_setup(setup, teardown)
    def test_expression_with_eval(self):
	expressions = { "ENV.$var.bleh|www": "ENV.a.bleh|www", }	
	self.loader.env_vars = { 'var': 'a' }

	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    # might need to test later
    def test_ws(self):
	pass

if __name__ == '__main__':
    nose.main()
