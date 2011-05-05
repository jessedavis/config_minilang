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
    # TODO: this needs to be reset before every invocation, right now
    # it'll persist between calls
    vars_section = None
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

    # override this to lookup values in other structures/services
    # TODO: modify var_eval to use this or something similar somehow
    def _resolve_value(self, subvalues_list):
	cur = self.env_vars
	result = None

	for subvalue in subvalues_list:
	    if subvalue in cur:
		cur = cur[subvalue]
	    if type(cur) is dict:
		continue
	    else:
		result = cur	

	return result

    # let resolve_value determine how and from where we'll pull value
    # let expression deal with operators
    def expression(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
        sub_exprs = dispatchList(self, subtree, buffer)

	# need to go through variable and expression and convert
	# to returning list

	# probably need to accomodate list of lists because of variable
	# and var_part

	#print sub_exprs

	try:
	    self.value = self._resolve_value(sub_exprs[0].split('.'))
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
	    # eat exception here, let expression and atom deal
	    # with undefined variables in more Pythonic terms
	    result = None

	return result

    def var_part(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	result = None
	    varpart_list = dispatchList(self, subtree, buffer)
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
	self.vars_section = getString(parseinfo, buffer)
	# return for debugging purposes (for now)	    
	return getString(parseinfo, buffer)

    def ws(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	return getString(parseinfo, buffer)
