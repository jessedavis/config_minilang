from distutils.core import setup

setup(name='config_minilang',
      version='0.0.1',
      author='Jesse Davis',
      author_email='jesse.michael.davis@gmail.com',
      url='https://github.com/jessedavis/config-minilang/',
      packages=['config_minilang'],
      package_dir={'config_minilang': 'config_minilang'},
      scripts=['bin/config_parser'],
     )
