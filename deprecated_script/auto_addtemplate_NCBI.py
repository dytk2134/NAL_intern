#! /usr/local/bin/python2.7
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

import sys
import re
import logging
import glob
import subprocess, shlex
import os
import ast
__version__ = '1.0'

def NCBI_template(infor_line, flatfile_to_json, biotype, type_dict):
    NCBI_template_dict = dict()
    # protein_coding: flatfile_to_json, data,$gff, type, gggsss, version, Genus_species ,link
    NCBI_template_dict["protein_coding"] = "perl %(flatfile_to_json)s --clientConfig \'{ \"description\": \"product, note, description\" }\' --out %(data)s --gff %(gff)s --arrowheadClass trellis-arrowhead --getSubfeatures --subfeatureClasses \'{\"wholeCDS\": null, \"CDS\":\"primary_gene_set-cds\", \"UTR\": \"primary_gene_set-utr\", \"exon\":\"container-100pct\"}\' --cssClass container-16px --type %(type)s --trackLabel %(gggsss)s_current_models --key \"NCBI Predicted protein coding genes, Annotation Release %(version)s\" --config \'{ \"category\": \"NCBI Annotation Release %(version)s/1. Gene Sets/Protein Coding\", \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\", \"Note\":\"Some genes may have non-coding transcripts\" }}\'"
    # lncRNA: $flatfile_to_json, $data,$gff, $type, $gggsss, $version, $Genus_species ,$link
    NCBI_template_dict["lncRNA"] = "perl %(flatfile_to_json)s --clientConfig \'{ \"description\": \"product, note, description\" }\' --out %(data)s --gff %(gff)s --arrowheadClass trellis-arrowhead --getSubfeatures --subfeatureClasses \'{\"wholeCDS\": null, \"CDS\":\"gnomon_CDS\", \"UTR\": \"gnomon_UTR\", \"exon\":\"container-100pct\"}\' --cssClass container-16px --type %(type)s --trackLabel NCBI_Annotation_Release_%(version)s_lncRNA --key \"NCBI Predicted lncRNA, Annotation Release %(version)s\" --config \'{ \"category\": \"NCBI Annotation Release %(version)s/1. Gene Sets/Noncoding\" , \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\"}}\'"
    # pseudogene: $flatfile_to_json, $data, $gff,$type, $version, $Genus_species, $version, $link
    NCBI_template_dict["pseudogene"] = "perl %(flatfile_to_json)s --out %(data)s --gff %(gff)s --arrowheadClass trellis-arrowhead --getSubfeatures --subfeatureClasses \'{\"wholeCDS\": null, \"CDS\":\"gnomon_CDS\", \"UTR\": \"gnomon_UTR\", \"exon\":\"container-100pct\"}\' --cssClass container-16px --type %(type)s --trackLabel NCBI_Annotation_Release_%(version)s_Pseudogene --key \"NCBI Predicted pseudogenes, Annotation Release %(version)s\" --config \'{ \"category\": \"NCBI Annotation Release %(version)s/1. Gene Sets/Pseudogenes\" , \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\"}}\'"
    # tRNA: $flatfile_to_json, $data,$gff, $type, $version, $Genus_species, $version, $link
    NCBI_template_dict["tRNA"] = "perl %(flatfile_to_json)s --out %(data)s --gff %(gff)s --arrowheadClass trellis-arrowhead --getSubfeatures --subfeatureClasses \'{\"wholeCDS\": null, \"CDS\":\"gnomon_CDS\", \"UTR\": \"gnomon_UTR\", \"exon\":\"container-100pct\"}\' --cssClass container-16px --type %(type)s --trackLabel NCBI_Annotation_Release_%(version)s_tRNA --key \"NCBI Predicted tRNAs, Annotation Release %(version)s\" --config '{ \"category\": \"NCBI Annotation Release %(version)s/1. Gene Sets/Noncoding\" , \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\"}}\'"
    # rRNA: $flatfile_to_json, $data,$gff, $type, $version, $Genus_species, $version, $link
    NCBI_template_dict["rRNA"] = "perl %(flatfile_to_json)s --clientConfig \'{ \"description\": \"product, note, description\" }\' --out %(data)s --gff %(gff)s --arrowheadClass trellis-arrowhead --getSubfeatures --subfeatureClasses \'{\"wholeCDS\": null, \"CDS\":\"gnomon_CDS\", \"UTR\": \"gnomon_UTR\", \"exon\":\"container-100pct\"}\' --cssClass container-16px --type %(type)s --trackLabel NCBI_Annotation_Release_%(version)s_rRNA --key \"NCBI Predicted rRNAs, Annotation Release %(version)s\" --config \'{ \"category\": \"NCBI Annotation Release %(version)s/1. Gene Sets/Noncoding\" , \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\"}}\'"
    # match
    NCBI_template_dict["match"] = "perl %(flatfile_to_json)s --out %(data)s --gff %(gff)s --arrowheadClass webapollo-arrowhead --cssClass container-10px --type %(type)s --trackLabel NCBI_Annotation_Release_%(version)s_match --key \"match evidence from NCBI Annotation Release %(version)s\" --config \'{ \"category\": \"NCBI Annotation Release %(version)s/2. Evidence\" , \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\"}}\'"
    # cDNA_match
    NCBI_template_dict["cDNA_match"] = "perl %(flatfile_to_json)s --out %(data)s --gff %(gff)s --arrowheadClass webapollo-arrowhead --cssClass container-10px --type %(type)s --trackLabel NCBI_Annotation_Release_%(version)s_cDNA_match --key \"cDNA match evidence from NCBI Annotation Release %(version)s\" --config \'{ \"category\": \"NCBI Annotation Release %(version)s/2. Evidence\" , \"metadata\": {\"Data description\": \"ftp://ftp.ncbi.nlm.nih.gov/genomes/%(Genus_species)s/README_CURRENT_RELEASE\", \"Data source\": \"%(link)s\", \"Data provider\": \"NCBI\", \"Method\": \"http://www.ncbi.nlm.nih.gov/genome/annotation_euk/process/\"}}\'"
    
    template = None
    d = {
        "flatfile_to_json":flatfile_to_json,
        "data":infor_line[5],
        "gff":infor_line[4],
        "type":None,
        "gggsss":infor_line[1],
        "version":infor_line[3],
        "Genus_species":infor_line[0],
        "link":infor_line[2]
    }
    if biotype in type_dict:
        d["type"] = type_dict[biotype]
        template = NCBI_template_dict[biotype] % d
    return template



if __name__ == '__main__':
    logger_stderr = logging.getLogger(__name__+'stderr')
    logger_stderr.setLevel(logging.INFO)
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger_stderr.addHandler(stderr_handler)
    logger_null = logging.getLogger(__name__+'null')
    null_handler = logging.NullHandler()
    logger_null.addHandler(null_handler)
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\
    This script will :
    1. run parse_and_separate_ncbi_gff3_by_gene_biotype.pl to split an NCBI annotation file by biotype
    2. get biotype from the filename (assume the filename is [gggsss]_[biotype].gff3) and then generate a flatfile to json template
    3. run flatfile-to-json.pl to add information to trackList.json

    Input file (6 column, tab-separated values):
    [Organism name] [gggsss] [NCBI genome assembly URL] [Annotation Release version] [absolute path to gff3 file] [absolute path to jbrowse/data]

    Quick start:
    python2.7 auto_addtemplate_NCBI.py -info information.tsv -path1 /home/script/flatfile-to-json.pl -path2 /home/script/parse_and_separate_ncbi_gff3_by_gene_biotype.pl
    """))

    parser.add_argument('-info', '--information', type=str, help='information about the file to add into the trackList.json. (tab delimited)', required=True)
    parser.add_argument('-path1', '--flatfile_to_json', type=str, help='absolute path to flatfile-to-json.pl', required=True)
    parser.add_argument('-path2', '--parse_and_separate_ncbi_gff3_by_gene_biotype', type=str, help='absolute path to parse_and_separate_ncbi_gff3_by_gene_biotype.pl', required=True)
    parser.add_argument('-protein_coding', '--protein_coding_gff', type=str, default="mRNA,transcript", help='feature types in [gggsss]_protein_coding Gff3 file to process, default: mRNA,transcript')
    parser.add_argument('-lncRNA', '--lncRNA_gff', type=str, default="lnc_RNA", help='feature types in [gggsss]_lncRNA Gff3 file to process, default: lnc_RNA')
    parser.add_argument('-pseudogene', '--pseudogene_gff', type=str, default="pseudogene", help='feature types in [gggsss]_pseudogene Gff3 file to process, default: pseudogene')
    parser.add_argument('-tRNA', '--tRNA_gff', type=str, default="tRNA", help='feature types in [gggsss]_tRNA Gff3 file to process, default: tRNA')
    parser.add_argument('-rRNA', '--rRNA_gff', type=str, default="rRNA", help='feature types in [gggsss]_rRNA Gff3 file to process, default: rRNA')
    parser.add_argument('-match', '--match_gff', type=str, default="match", help='feature types in [gggsss]_match Gff3 file to process, default: match')
    parser.add_argument('-cDNA_match', '--cDNA_match_gff', default="cDNA_match", type=str, help='feature types in [gggsss]_cDNA_match Gff3 file to process, default: cDNA_match')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    type_dict = {
        "protein_coding": args.protein_coding_gff,
        "lncRNA": args.lncRNA_gff,
        "pseudogene": args.pseudogene_gff,
        "tRNA": args.tRNA_gff,
        "rRNA": args.rRNA_gff,
        "match": args.match_gff,
        "cDNA_match": args.cDNA_match_gff
    }
    
    current_path = os.getcwd() + "/"

    # 
    NCBI_biotypes = ["protein_coding", "lncRNA", "pseudogene", "tRNA", "rRNA", "match", "cDNA_match"]
    with open(args.information, 'r') as in_f:
        for line in in_f:
            if line.startswith == '#':
                continue
            line = line.strip()
            lines = line.split("\t")
            if len(lines) == 6:
                # run the script to split an NCBI annotation file by biotype
                gff3_path = os.path.dirname(os.path.abspath(lines[4])) + "/"
                os.chdir(gff3_path)
                subprocess.Popen(['perl', args.parse_and_separate_ncbi_gff3_by_gene_biotype, lines[4], lines[1]]).wait()
                for gff_file in glob.glob(gff3_path + lines[1] + '*'):
                    filename = os.path.splitext(os.path.basename(gff_file))[0]
                    try:
                        biotype = filename.replace(lines[1]+"_","")
                        if biotype in NCBI_biotypes:
                            template = NCBI_template(lines, args.flatfile_to_json, biotype, type_dict)
                            if template != None:
                                cmd = shlex.split(template)
                                subprocess.Popen(cmd)
                        else:
                            continue
                    except:
                        continue    

                     


    


    


