# What It Is #

A mini-language to embed within config files.  Values for the
expressions will be passed in as a dictionary (for now).

## Overview ##

At previous jobs, I've had to manage plenty of configuration files.
The configuration files will usually be the same except for different 
values for different environments (production, QA, integration, etc).
Templatizing the configuration file is normal, but with a lot of 
environments, you now have a lot of input files.

So, shrink the input files that contain the values.  Above all, DRY 
(Don't Repeat Yourself).  Expressions that can be evaluated can be
called from other templating engines (for the first iteration of 
this tool, jinga2 is being used).

## Examples ##

Given a YAML file, envs.yaml:

    qa: {
      prefix: 'qa',
    },
    int: {
      prefix: 'integration',
    },
    prod: {
      prefix: 'www',
    }, 

and a template, template.html:

    <html>
      <body>
        You're at http://{{"ENV.$env.prefix"|myfilter}}.example.com.
      <body>
    </html>

you can execute the generator with different values for $env.

    ./config_parsery.py env=qa

    <html>
      <body>
        You're at http://qa.example.com.
      <body>
    </html>

    ./config_parsery.py env=prod

    <html>
      <body>
        You're at http://www.example.com.
      <body>
    </html>

Two operators are allowed:

  * | - if operator
    If the first value can't be defined, use the second.  These can be
    chained.

    Given:
    a: '1',
    b: '2',

    $a|$b|c = 1, 2 if a were blank, c if b was also blank.

  * \+ - string concatenation
    Join the expressions together.  Can be used for normal strings as 
    well.

    Given:
    a: 'this little ',

    $a+'piggy' = 'this little piggy'

Literals are backscaped.  Allowed literals are . (period), $, | and + .

    \.+$a = .1

To insert an empty string, use "None", "Empty", "NONE" or "EMPTY".

    $d|None = ''

## Documentation ##

./config_parser.py [-d|-v|-q] [-f config_file] 
    file_to_parse.template list_of_variables

  * -d | --debug , -v | --verbose , -q | --quiet
     Set the log level.

  * -f | --cfg_file 
     Specify a file that matches tags to files containing the values.

     By default, this looks like:

     # Each tag to be used as a variable source in ConfigLoader must be 
     # defined here.  If an absolute path is not specified, the current
     # directory is assumed.

     [file_locations]

     ENV: envs.yaml

     This file would be read for a expression starting with ENV, like:

     ENV.$env.prefix

  * Extra variables can be defined on the command line, separate by
    commas:

    foo=bar,x=2

### TODO ###

Abstract out the templating engine.  I looked at mako vs. jinga2, and 
was only able to successfully use jinga2.  I'd like to also configure
jinga2 correctly so that I don't pepper the templates with the 
myfilter filter tag.

Abstract out the lookup function so JSON, etc. can be used for the 
value files.
