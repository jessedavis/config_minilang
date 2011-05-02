#!/usr/bin/env python

config_minilang = r"""
root           := expression
expression     := atom, (ws, op, ws, atom)*
op             := if_op / concat_op
if_op          := '|'
concat_op      := '+'
atom           := literal / variable
<literal>      := '\\', [.$|+]
variable       := (var_source,'.')?, var_part
var_part       := (var / var_eval),('.', ( var / var_eval ))*
var            := [a-zA-Z], [a-zA-Z0-9_]*
var_eval       := '$', var
var_source     := [A-Z_]+
<ws>           := [ \t\n\r]*
"""
