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

class test_config_loader(unittest.TestCase):

    parser = None
    loader = None
    test_values = {}

    @classmethod
    def setUpClass(self):
	self.parser = simpleparse.parser.Parser(config_grammar.config_minilang, 'root')
	self.loader = ConfigLoader()

    def setUp(self):
	# self.loader.env_vars is a reference, sincy Python
	# passes references-to-objects by value (i.e. pass by value, but
	# everything's an object, and the value is a reference to the 
	# object) - hence, always create a brancd new fixture for each
	# test
	self.loader.env_vars = dict({
	    'ENV': { 
		'qa': {
		    'val': 'a',
		},
		'production': {
		    'val': 'b',
		},
		'a': 'apple',
	    },
	    # TODO: future work to support $$var 
	    # calling $var with var = a will print a, of course
	    #'a': 'organicapple',
	})

    def tearDown(self):
	self.loader.env_vars.clear()

    @classmethod
    def tearDownAll(self):
	pass

    def test_variable(self):
	variables = {
            "hi": "hi",
            "ENV.a": "apple",
            "ENV.qa.val": "a",
	}
	for variable, value in variables.iteritems():
	    self.parser.parse(variable, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    def test_variable_source(self):
	strings = { "ENV.bleh": "ENV",
	            "ENVTOO.bleh.bluh": "ENVTOO",
	}	
	for string, env in strings.iteritems():
	    self.parser.parse(string, processor=self.loader)
	    self.assertEqual(env, self.loader.vars_section)

    def test_eval_variables(self):

	expressions = { '$var': 'a',
	                'bleh.$var': None,
	                'ENV.$var': 'apple',
			'ENV.$var.bleh': None,
	                'ENV.$env.$second': 'a',
	              }
	self.loader.env_vars['var'] = 'a'
	self.loader.env_vars['env'] = 'qa'
	self.loader.env_vars['second'] = 'val'

	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    def test_eval_variable_error(self):
	expressions = { '$unknownvar': 'b', }

	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(None, self.loader.value)

    def test_expression_if(self):
	expressions = {
	    "ENV.qa.val|www": "a",
	    "ENV.bleh.bleh|www": "www",
	}
	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    def test_expression_concat(self):
	expressions = {
	    "ENV.production.val+lock": "block",
	    "ENV.bleh.bleh+www": None,
	}
	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    def test_expression_with_eval(self):
	expressions = { "ENV.$var.bleh|www": "www",
		        "ENV.$var.val|www" : "a",
			"ENV.$var.val+cow" : "acow", }	
	self.loader.env_vars['var'] = 'qa'

	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    def test_expression_complex(self):
	expressions = {
	    "www": "www",
	    '$var': None,
	    'ENV.$var': None,
	    "ENV.qa.not_here|www|blank": "www",
	    'ENV.qa.not_here|$unknown|blank': "blank",
	    "ENV.qa.val+duck": "aduck",
	    "ENV.qa.val|www+duck": "a",
	    "ENV.qa.not_here|www+duck": "wwwduck",
	}	
	for expression, value in expressions.iteritems():
	    self.parser.parse(expression, processor=self.loader)
	    self.assertEqual(value, self.loader.value)

    # might need to test later
    def test_ws(self):
	pass

if __name__ == '__main__':
    nose.main()
