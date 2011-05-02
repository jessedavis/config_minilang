#!/usr/bin/env python

import logging
import simpleparse
from simpleparse.common import strings, numbers
from simpleparse.dispatchprocessor import *

import config_grammar

class ConfigLoader(DispatchProcessor):
    """Parses the expression and returns back a value if it can be 
       resolved."""

    value = None
    log = None
    env_vars = {}

    def __init__(self, log=None, env_vars=None, *args, **kwargs):
	#super(self.__class__, self).__init__(*args, **kwargs)

	if log is None:
	    self.log = logging.getLogger(self.__class__.__name__)
	else:
	    self.log = log

	# see http://stackoverflow.com/questions/423379/global-variables-in-python
	# as to why we pass in our own vars
	self.env_vars = env_vars

    def expression(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
        sub_exprs = dispatchList(self, subtree, buffer)

	try:
	    self.value = ''.join(sub_exprs)
	except TypeError as e:
	    # might want something less than error here, since we're
	    # handling the error
	    self.log.error("Error evaluating expression: %s" % e)
	    self.value = None

    def op(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
	return dispatch(self, subtree[0], buffer)

    def if_op(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	# TODO: work in a enum style return here
	#
	return '|'

    def concat_op(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	# TODO: work in a enum style return here
	#
	return '+'

    def atom(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
	return dispatch(self, subtree[0], buffer)

    def literal(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
	return dispatch(self, subtree[0], buffer)

    def variable(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	try:
	    subvar_list = dispatchList(self, subtree, buffer)
	    if len(subvar_list) == 1:
		result =  subvar_list[0]
	    else:
		result = '.'.join(subvar_list)
	except NameError:
	    self.log.error("Part of %s not able to be evaluated." %
	                   buffer)
	    # eat exception here, let expression, clause and atom deal
	    # with undefined variables in more Pythonic terms
	    result = None

	return result

    def var_part(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	result = None
	try:
	    varpart_list = dispatchList(self, subtree, buffer)
	    if len(varpart_list) == 1:
		result = varpart_list[0]
	    else:
		result = '.'.join(varpart_list)
	except NameError:
	    self.log.error("Part of %s not able to be evaluated." %
	                   buffer)
	    raise

	return result
	    
    def var(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
	return getString(parseinfo, buffer)

    def var_eval(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	value = None
	try:
	    # peel off the $ in front of the variable
	    value = eval(getString((tag, left + 1, right, subtree),
	                           buffer), 
	                 self.env_vars)
	except NameError:
	    self.log.error(("Unable to find value of %s in "
	                   "current context.") %
	                   buffer[left+1:right])
	    raise
	    
	return value

    def var_source(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	# TODO: may need to work env lookup somehow here
	#
	return getString(parseinfo, buffer)

    def ws(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	return getString(parseinfo, buffer)


if __name__ == '__main__':
    parser = simpleparse.parser.Parser(config_grammar.config_minilang, 'root')

    log = logging.getLogger("test")
    log_level = logging.DEBUG

    log.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    log_format = "%(asctime)s - %(levelname)s: %(message)s"
    handler.setFormatter(logging.Formatter(log_format))
    log.addHandler(handler)

    loader = ConfigLoader(log=log)

    # for var_eval, this will probably meld somehow into the population
    # of hashes from yamls
    # see http://effbot.org/zone/librarybook-core-eval.htm for more ideas
    #scrubbed_env = {"__builtins__": {}}

    env = 'iamqa'

    parser.parse("ENV.bleh.$env", processor=loader);

    print "loader value = %s" % loader.value
