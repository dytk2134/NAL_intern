#! /usr/local/bin/python2.7
# Copyright (C) 2018  Li-Mei Chiang <dytk2134 [at] gmail [dot] com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

import argparse
import re
from textwrap import dedent
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

__version__ = '1.0'

import argparse, sys
import subprocess
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
python /app/data/limei.chiang/auto_adduser.py -dbuser web_apollo_users_admin -dbname test_users -infile /app/data/limei.chiang/test_user.txt -host apollo-stage.nal.usda.gov -adduser /app/data/limei.chiang/adduser.py
''')
parser.add_argument('-adduser', help="path to the adduser.py", required=True)
parser.add_argument('-infile', help="output file from users", required=True)
parser.add_argument('-dbuser', help="Username used to connect database", required=True)
parser.add_argument('-dbname', help="Database name to be connected", required=True)
parser.add_argument('-host', help="Host name or IP of database server (Default: localhost)", required=False, default='localhost')
parser.add_argument('-perm', help="Permission of the new user (Default: 3)", required=False, default='3')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

args = parser.parse_args()

user_lists = []
with open(args.infile, 'r') as in_f:
    for line in in_f:
        line = line.strip()
        lines = line.split("\t")
        user_lists.append(lines)

# line_number user_name user_password
for lines in user_lists:
    cmd = ['python', args.adduser, '-dbuser', args.dbuser, '-dbname', args.dbname, '-user', lines[1], '-pwd', lines[2], '-host', args.host, '-perm', args.perm]
    subprocess.Popen(cmd).wait()
