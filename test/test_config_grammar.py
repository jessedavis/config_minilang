#!/usr/bin/env python

'''
Tests for config_grammar.

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

from config_minilang import config_grammar

class test_config_grammar(unittest.TestCase):

    parser = None

    @classmethod
    def setUpClass(self):
	self.parser = simpleparse.parser.Parser(config_grammar.config_minilang)

    @classmethod
    def tearDownAll(self):
	pass

    @nottest
    def parse_test_strings(self, strings_to_test, production):
	for string in strings_to_test:
	    success, children, nextchar = self.parser.parse(string, 
	                                      production=production)
	    assert success and nextchar == len(string), (
		"Wasn't able to parse %s as a %s "
		"(%s chars parsed of %s), returned value was %s"
		) % ( repr(string), production, nextchar, len(string), 
		      (success, children, nextchar))

    def test_expression(self):
	strings = [ 
	    'a|b',
	    'a+b',
	    'ENV.$env|b',
	    'ENV.a|b',
	    'ENV.$env.a|b',
	    'ENV.$env+b',
	    'ENV.a+b',
	    'ENV.$env.a+b',
	    'ENV.$env |b',
	    'ENV.$env| b',
	    'ENV.$env | b',
	    'ENV.$env | b | c',
	]
	self.parse_test_strings(strings, "expression")

    def test_literal(self):
	strings = [ 
	    '\.', '\$', '\|', '\+',
	]
	self.parse_test_strings(strings, "literal")

    def test_variable(self):
	strings = [ 
	    "bleh",
	    '$bleh',
	    'bleh.$bleh',
	    '$bleh.$bleh',
	    "ENV.bleh",
	    'ENV.bleh.$bleh',
	    'ENV.$bleh.bleh',
	]
	self.parse_test_strings(strings, "variable")

    def test_none(self):
	strings = [

	]
	self.parse_test_strings(strings, "none")

    def test_var(self):
	strings = [ 
	    "bleh",
	]
	self.parse_test_strings(strings, "var")

    def test_var_eval(self):
	strings = [ 
	    '$bleh',
	]
	self.parse_test_strings(strings, "var_eval")

    def test_var_source(self):
	strings = [ 
	    "ENV",
	    "ENV_TOO",
	]
	self.parse_test_strings(strings, "var_source")

if __name__ == '__main__':
    nose.main()
