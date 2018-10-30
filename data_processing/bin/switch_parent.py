#! /usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)

import os
import re
import sys
import subprocess
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

__version__ = '1.0.0'

def find_parents(target, in_gff3):
    parents = dict() # {ParentID: [Parent, children1, children2]}
    missing_parent = list()
    with open(in_gff3, 'r') as in_f:
        for line in in_f:
            line = line.strip()
            if line:
                if not line.startswith('#'):
                    tokens = line.split('\t')
                    if len(tokens) == 9:
                        attributes = dict(re.findall('([^=;]+)=([^=;\n]+)', tokens[8]))
                        feature = {
                            'ID': None,
                            'type': tokens[2],
                            'children': [],
                            'parent': [],
                            'root': None,
                            'attributes': attributes
                        }
                        find_parent = False
                        if 'ID' in attributes:
                            feature['ID'] = attributes['ID']
                            if attributes['ID'] not in parents:
                                parents[attributes['ID']] = list()
                            parents[attributes['ID']].append(feature)
                            if 'Parent' not in attributes:
                                # find root feature
                                find_parent = True
                                feature['root'] = attributes['ID']

                                if tokens[2] == target:
                                    logger.error('There is no Parent attribute in target feature.')
                                    sys.exit(1)
                            else:
                                # find children feature
                                parent_list = attributes['Parent'].split(',')
                                for p in parent_list:
                                    if p in parents:
                                        find_parent = True
                                        feature['parent'].extend(parents[p])
                                        feature['root'] = parents[p][0]['root']
                                        parents[p][0]['children'].append(feature)
                            if find_parent == False:
                                missing_parent.append(feature)
                                continue

    for feature in missing_parent:
        for p in feature['attributes']['Parent']:
            if p in parents:
                feature['parent'].extend(parents[p])
                feature['root'] = parents[p][0]['root']
                parents[p][0]['children'].append(feature)
    return parents

def find_model(root):
    models = [root]
    for child in root['children']:
        models.append(child)
        models.extend(find_model(child))
    return models



def find_target_ID(parent, parent_ID, parent_dict):
    target_ID = None
    root_ID = parent_dict[parent_ID][0]['root']
    models = find_model(parent_dict[root_ID][0])
    for feature in models:
        if feature['type'] == parent:
            try:
                target_ID = feature['ID']
                return target_ID
            except KeyError:
                logger.error('Parent feature should have ID attribute')
                sys.exit(1)
        else:
            continue

    return target_ID

def switch_parent(target, parent, in_gff3, out_gff3):
    # The target feature types that you want to change its parent. e.g. stop_colon_read_through
    # The new type of parent feature for target feature types. e.g. mRNA
    # parents = {'ID':{'mRNA':[[],[],[]], 'CDS': [[],[]]}}
    parents = find_parents(target, in_gff3)
    with open(out_gff3, 'w') as out_f:
        with open(in_gff3, 'r') as in_f:
            for line in in_f:
                line = line.strip()
                if line.startswith('#'):
                    out_f.write(line + '\n')
                else:
                    tokens = line.split('\t')
                    if len(tokens) == 9:
                        if tokens[2] == target:
                            new_parent = set()
                            attributes = dict(re.findall('([^=;]+)=([^=;\n]+)', tokens[8]))
                            # old parent ID list
                            parent_list = attributes['Parent'].split(',')
                            if len(parent_list) > 1:
                                logger.warning('Target feature has multiple parents.\n%s' % (line))
                            for p in parent_list:
                                if p in parents:
                                    target_ID = find_target_ID(parent, p, parents)
                                    if target_ID:
                                        new_parent.add(target_ID)
                                else:
                                    logger.error('Failed to find %s in the gff3 file.' % (p))
                                    sys.exit(1)
                            
                            if len(new_parent) == 0:
                                logger.error('Failed to find %s in the target model.\n%s' % (parent, line))
                                sys.exit(1)
                            attributes['Parent'] = ','.join(new_parent)
                            attributes_list = list()
                            for key in attributes:
                                attributes_list.append('%s=%s' % (str(key), str(attributes[key])))
                            # update cloumn 9
                            tokens[8] = ';'.join(attributes_list)
                            out_f.write('\t'.join(tokens) + '\n')
                        else:
                            out_f.write(line + '\n')
                    else:
                        logger.error('Features should contain 9 fields.\n%s' % line)
                        sys.exit(0)


def main(target, parent, gff3, postfix):
    gff3_filename, gff3_extension = os.path.splitext(os.path.abspath(gff3))
    out_gff3 = '%s%s%s' % (gff3_filename, postfix, gff3_extension)
    switch_parent(target=target, parent=parent, in_gff3=gff3, out_gff3=out_gff3)


if __name__ == '__main__':
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\

    This script is aim to change the Parent of the target feature type to another feature.
    Usage:
    %(prog)s -t stop_colon_read_through -p mRNA -g example.gff3
    """))

    parser.add_argument('-t', '--target', type=str, help='The target feature types that you want to change its parent. e.g. stop_colon_read_through', required=True)
    parser.add_argument('-p', '--parent', type=str, help='The new type of parent feature for target feature types. e.g. mRNA', required=True)
    parser.add_argument('-g', '--input_gff', nargs='+', type=str, help='List one or more GFF3 files to be updated.', required=True)
    parser.add_argument('-postfix', '--postfix', default='_mod', help='The filename postfix for modified features (default: "_mod")')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    for gff3 in args.input_gff:
        main(target=args.target, parent=args.parent, gff3=gff3, postfix=args.postfix)



