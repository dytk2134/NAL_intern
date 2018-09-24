#!/usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)

import logging
import subprocess
import os
import sys
import re


__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

def assembly_report_to_dict(old_id, new_id, report):
    logger.info('Reading alignment data from: %s...', report)
    replace_id = {
        'sn': 'Sequence-Name',
        'ga': 'GenBank-Accn',
        'ra': 'RefSeq-Accn'
    }

    assembly_report_dict = {}
    ID_column = {
        'sn': 0,
        'ga': 4,
        'ra': 6
    }
    with open(report, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line[0] != "#":
                lines = line.split("\t")
                assembly_report_dict[lines[ID_column[old_id]]] = lines[ID_column[new_id]]
    return assembl_report_dict

def main(in_gff3, old_id, new_id, report):
    assembl_report_dict = assembl_report_dict(old_id, new_id, report)
    # List of old gff3 files
    for filename in in_gff3:
        gff_root, gff_ext = os.path.splitext(filename)
        output_file_update = gff_root + "_update" + gff_ext
        output_file_remove = gff_root + "_remove" + gff_ext
        output_update = open(output_file_update, "w")
        output_remove = open(output_file_remove, "w")
        updated_count = 0
        removed_count = 0
        logger.info('Processing GFF3: %s', filename)
        logger.info('Replacing Sequence ID from %s to %s ...' % (replace_id[old_id], replace_id[new_id]))

        with open(filename,"r") as gff_file:
            for gff_line in gff_file:
                if gff_line[0] == '#':
                    output_update.write(gff_line)
                else:
                    gff_lines = gff_line.split("\t")
                    try:
                        gff_lines[0] = assembl_report_dict[gff_lines[0]]
                        Oline = "\t".join(gff_lines)
                        output_update.write(Oline)
                        updated_count += 1
                    except:
                        Oline = "\t".join(gff_lines)
                        output_remove.write(Oline)
                        removed_count += 1

        output_update.close()
        output_remove.close()
        logger.info(' Total features: %d', updated_count + removed_count)
        logger.info(' Updated features: %d', updated_count)
        logger.info(' Removed features: %d', removed_count)


if __name__ == '__main__':
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\
    This script is for updating scaffold ID in old gff3 file from the old ID to the new ID based on the assembly report from NCBI.

    Usage:
    python %(prog)s -in old1.gff3 old2.gff3 -old ga -new ra -r GCA_000344095.1_Aros_1.0_assembly_report.txt
    """))
    # argument
    parser.add_argument('-in', '--in_gff3', nargs='+', type=str, help='List one or more GFF3 files to be updated.', required=True)
    parser.add_argument('-old', '--old_id', type=str, help='{0:s}\n\t{1:s}\n\t{2:s}\n\t{3:s}'.format('The source of old sequence id: ','"sn" - Sequence-Name in assembly report(column 1);', '"ga" - GenBank-Accn in assembly report(column 5);', '"ra" - RefSeq-Accn in assembly report(column 7);'), required=True)
    parser.add_argument('-new', '--new_id', type=str, help='{0:s}\n\t{1:s}\n\t{2:s}\n\t{3:s}'.format('The source of new sequence id: ','"sn" - Sequence-Name in assembly report(column 1);', '"ga" - GenBank-Accn in assembly report(column 5);', '"ra" - RefSeq-Accn in assembly report(column 7);'), required=True)
    parser.add_argument('-r', '--assembly_report', type=str, help='The assembly report from NCBI.', required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    replace_id_column = ['sn', 'ga', 'ra']
    if args.old_id not in replace_id_column:
        logger.error('Your source of old sequence id is "%s". This must be one of %s!' % (args.old_id, str(replace_id_column)))
        sys.exit(1)
    if args.new_id not in replace_id_column:
        logger.error('Your source of new sequence id is "%s". This must be one of %s!' % (args.new_id, str(replace_id_column)))
        sys.exit(1)
    main(in_gff3=args.in_gff3 , old_id=args.old, new_id=args.new_id, report=args.assembly_report)