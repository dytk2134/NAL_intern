#! /usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)

import os
import re
import sys
import subprocess
import logging
import uuid
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

__version__ = '1.0.0'

def add_parent(target, parent, in_gff3, out_gff3):
    with open(out_gff3, 'w') as out_f:
        with open(in_gff3, 'r') as in_f:
            for line in in_f:
                line = line.strip()
                if line.startswith('#'):
                    out_f.write(line + '\n')
                else:
                    tokens = line.split('\t')
                    if len(tokens) == 9:
                        if tokens[2] in target:
                            attributes = dict(re.findall('([^=;]+)=([^=;\n]+)', tokens[8]))
                            tokens[8] = attributes
                            if 'Parent' in attributes:
                                logger.warning('The target type of feature already has Parent attribute. Won\'t add parent to this feature.\n %s' % line)
                            else:
                                parent_line = list(tokens)
                                # parent feature type
                                parent_line[2] = parent
                                # parent ID
                                parent_id = str(uuid.uuid1())
                                parent_line[8] = dict(parent_line[8])
                                parent_line[8]['ID'] = parent_id
                                # write out parent feature
                                attributes_list = list()
                                for key in parent_line[8]:
                                    attributes_list.append('%s=%s' % (str(key), str(parent_line[8][key])))
                                parent_line[8] = ';'.join(attributes_list)
                                out_f.write('\t'.join(parent_line) + '\n')
                                attributes_list = list()
                                # add Parent attribute
                                tokens[8]['Parent'] = parent_id
                                for key in tokens[8]:
                                    attributes_list.append('%s=%s' % (str(key), str(tokens[8][key])))
                                tokens[8] = ';'.join(attributes_list)
                                out_f.write('\t'.join(tokens) + '\n')
                        else:
                            out_f.write(line + '\n')
                    else:
                        logger.error('Features should contain 9 fields.\n%s' % line)
                        sys.exit(0)


def main(target, parent, gff3, postfix):
    gff3_filename, gff3_extension = os.path.splitext(os.path.basename(gff3))
    out_gff3 = '%s%s%s' % (gff3_filename, postfix, gff3_extension)
    target_set = set()
    target = target.replace(' ', '')
    target_set.update(target.split(','))
    add_parent(target=target_set, parent=parent, in_gff3=gff3, out_gff3=out_gff3)

if __name__ == '__main__':
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\

    This script is aim to add a parent feature for target types of feature.
    Usage:
    %(prog)s -t insertion -p sequence_alteration -g example.gff3
    """))

    parser.add_argument('-t', '--target', type=str, help='List one or more feature types for adding parent feature. e.g. insertion,deletion', required=True)
    parser.add_argument('-p', '--parent', type=str, help='Type of parent feature to add for target feature types. e.g. sequence_alteration', required=True)
    parser.add_argument('-g', '--input_gff', nargs='+', type=str, help='List one or more GFF3 files to be updated.', required=True)
    parser.add_argument('-postfix', '--postfix', default='_mod', help='The filename postfix for modified features (default: "_mod")')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    for gff3 in args.input_gff:
        logger.info('Processing %s' % (gff3))
        main(target=args.target, parent=args.parent, gff3=gff3, postfix=args.postfix)
