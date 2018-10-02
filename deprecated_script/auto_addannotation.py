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
import sys
import subprocess
import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

__version__ = '1.0'


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''

''')
parser.add_argument('-anno', help="path to the add_transcripts_from_gff3_to_annotations.pl", required=True)
parser.add_argument('-inuser', help="output file from users", required=True)
parser.add_argument('-U', help="url", required=True)
parser.add_argument('-infile', nargs='+',help="List of input files", required=True)
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
args = parser.parse_args()

user_dict = dict()
#username: password
with open(args.inuser, 'r') as in_f:
    for line in in_f:
        line = line.strip()
        lines = line.split("\t")
        user_dict[lines[1]] = lines[2]

# line_number user_name user_password
for inf in args.infile:
    owner = os.path.splitext(inf)[0].split("_")[-1]
    password = None
    if owner in user_dict:
        password = user_dict[owner]
    if password != None:
        cmd = ['perl', args.anno, '-U', args.U, '-u', owner,'-p',password,'-i',inf]
        print(' '.join(cmd))
        #subprocess.Popen(cmd).wait()
