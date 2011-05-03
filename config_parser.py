#!/usr/bin/env python

"""
"""

import ConfigParser
import logging
from optparse import OptionParser
import os
import sys

import simpleparse
import yaml

import config_grammar
from config_loader import ConfigLoader

def initialize_logging(logger_name='config_parser'):
    log = logging.getLogger(logger_name)
    log_level = logging.WARNING

    log.setLevel(log_level)
    handler = logging.StreamHandler()
    # send on everything
    handler.setLevel(logging.NOTSET)
    log_format = "%(asctime)s - %(levelname)s: %(message)s"
    handler.setFormatter(logging.Formatter(log_format))
    log.addHandler(handler)

    return log
    
def initialize_options(usage=None):
    cfg = os.path.join(os.environ['HOME'], '.config_parser.cfg') 
    parser = OptionParser()

    parser.set_usage(usage)
    parser.set_defaults(config_file=cfg)
    parser.add_option("-f", "--cfg_file", action="store", type="string",
		      dest="config_file", 
		      help='Config file, default: $HOME/.config_parser.cfg')
    parser.add_option("-d", dest="debug", action="store_true",
                      help="Print debugging info.")
    parser.add_option("-v", dest="verbose", action="store_true",
                      help="Print extra logging info.")
    parser.add_option("-q", dest="quiet", action="store_true",
                      help="Print no logging info.")

    return parser

def read_yaml_files(filename):
    config_section = 'file_locations'
    yaml_values = {}

    config = ConfigParser.ConfigParser()

    # default is options are lowercased
    # keep case sensitive because of our var source
    config.optionxform = str

    if filename not in config.read(filename):
	log.warning("Error reading config file %s, skipping." % filename)
	return yaml_values

    if not config.has_section(config_section):
	log.warning("No section %s in config file, skipping." % 
	            config_section)
	return yaml_values

    for tag, yaml_file in config.items(config_section):
	if not yaml_file.startswith(os.sep):
	    yaml_file = os.path.join(os.getcwd(), yaml_file)

	try: 
	    with open(yaml_file) as f:
		values_dict = yaml.load(f)
		yaml_values[tag] = values_dict	

	    log.info("Loaded YAML file, tag: %s, file: %s" %
		      (tag, yaml_file))
	except IOError as e: 
	    log.error("Error parsing YAML file: %s" % e)
		
    return yaml_values	    	

if __name__ == '__main__':

    cli_options = initialize_options("usage: %prog [options] file")

    (options, args) = cli_options.parse_args()
    if len(args) != 1:
	cli_options.error("No file to parse given.")

    log = initialize_logging(logger_name=sys.argv[0])
    
    if options.debug:
	log.setLevel(logging.DEBUG)
    if options.verbose:
	log.setLevel(logging.INFO)
    if options.quiet:
	log.setLevel(logging.ERROR)

    yaml_values = read_yaml_files(options.config_file)

    parser = simpleparse.parser.Parser(config_grammar.config_minilang, 
	                               'root')
    loader = ConfigLoader(log=log, env_vars=yaml_values)
