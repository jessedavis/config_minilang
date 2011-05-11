#!/usr/bin/env python

import logging
import simpleparse
from simpleparse.common import strings, numbers
from simpleparse.dispatchprocessor import *

import config_grammar

def flatten(list):
    if type(list) is not type([]):
	return [list]
    if list == []:
	return list
    return flatten(list[0]) + flatten(list[1:])
	
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

	self.log.debug("_resolve_value: subvalues_list = %s" % 
	               subvalues_list)

	# TODO: sort of a hack here, should be more elegant here
	# no lookup to be done, so just return first value
	if len(subvalues_list) == 1:
	    result = subvalues_list.pop()

	while len(subvalues_list) > 0:
	    subvalue = subvalues_list.pop(0)
	    if subvalue in cur.keys():
		if type(cur[subvalue]) is dict:
		    cur = cur[subvalue]
		    continue
		elif type(cur[subvalue]) == type(''):
		    result = cur[subvalue]
		else:
		    self.log.error("Invalid type encountered "
				   "in _resolve_value(), exiting.")
	    else:
		result = None

	self.log.debug("_resolve_value: result = %s" % result)

	return result

    def _resolve_expression(self, subexprs_list):
	# first resolve to RPN using Dijkstra's shunting yard algo
	# http://en.wikipedia.org/wiki/Shunting-yard_algorithm
	result = None
	op_stack = []
	token_list = []

	# work this into an enum later, value is precedence
	operators = {
	    '|': 0, 
	    '+': 1
	}
	
	# TODO: need to work in parentheses and error checking here
	# for broken expressions
	for subexpr in subexprs_list:
	    if type(subexpr) is list:
		token_list.append(subexpr)
	    elif subexpr in operators.keys():
		while len(op_stack) > 0 and \
		      ( operators[subexpr] <= 
			operators[op_stack[len(op_stack) - 1]]):
		    op2 = op_stack.pop()
		    token_list.append(op2)

		op_stack.append(subexpr) 
	    else:
		self.log.error("Unknown state in _resolve_expression")

	# no more tokens
	while len(op_stack) > 0:
	    token_list.append(op_stack.pop())

	self.log.debug("RPN of expression = %s" % token_list)

	# now compute the value of the RPN representation

	value_stack = []

	# TODO: need to work in parentheses and error checking here
	# for broken expressions
	for token in token_list:
	    if type(token) is list:
		# determine the final value of our operand
		value_stack.append(self._resolve_value(token))
	    elif token is '|':
		operand2 = value_stack.pop()
		operand1 = value_stack.pop()
		if operand1 is not None:
		    value_stack.append(operand1)
		else:
		    value_stack.append(operand2)
	    elif token is '+':
		operand2 = value_stack.pop()
		operand1 = value_stack.pop()
		if operand1 is None or operand2 is None:
		    value_stack.append(None)
		else:
		    value_stack.append(operand1 + operand2)
	    else:
		self.log.error("Unknown token type in _resolve_expression")

	    self.log.debug("token_list = %s, value_stack = %s" % 
			   (token_list, value_stack))

	result = value_stack.pop()
	
	return result

    # let resolve_value determine how and from where we'll pull value
    # let expression deal with operators
    def expression(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))
        sub_exprs = dispatchList(self, subtree, buffer)

	try:
	    self.value = self._resolve_expression(sub_exprs)
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

	# TODO: may want to inline atom in the grammar (<atom>) and return 
	# a list, using the construct below seems a litte weird with 
	# the use of [] in the other rules
	#return dispatchList(self, subtree, buffer)
	return dispatch(self, subtree[0], buffer)

    def literal(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	# literal and variable are equal in our grammar, so 
	# encapsulate the string representing the literal in a list
	# to allow expressions to just worry about processing lists

	# eat the \ in front of the literal
	return [ getString((tag, left + 1, right, subtree), buffer) ]

    def variable(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	result = []

	# eat exceptions here, let expression and atom deal
	# with undefined variables in more Pythonic terms
	try: 
	    subvar_list = dispatchList(self, subtree, buffer)
	    if None in subvar_list:
		self.log.error("None encountered as part of %s." %
		               buffer)
		result = []
	    else:
		# squash all parts of a variable down into one list
		result = flatten(subvar_list) 
	except NameError as e:
	    self.log.error("Cannot evaluate part of variable: %s" %
			   buffer)
	    result = []

	self.log.debug("variable: result = %s" % result)
	return result

    def var_part(self, parseinfo, buffer):
	tag, left, right, subtree = parseinfo
	self.log.debug(("%s : buffer = %s, (start, end) = (%d, %d), "
	               "subtree = %s") %
	               (tag, buffer, left, right, subtree))

	result = []
	varpart_list = dispatchList(self, subtree, buffer)
	if None in varpart_list:
	    error_msg = "Part of %s not able to be evaluated." % buffer
	    self.log.error(error_msg)
	    raise NameError(error_msg)
	else:
	    # squash all parts of a variable down into one list
	    result = flatten(varpart_list) 

	self.log.debug("var_part: result = %s" % result)

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
