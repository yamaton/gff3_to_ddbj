#!/usr/bin/env python
import argparse
import logging
import pathlib

import pkg_resources  # part of setuptools

from . import formatter
from . import transforms
from . import utils

_PROJ_NAME = "gff3toddbj"
_EXEC_NAME = "gff3-to-ddbj"
__version__ = pkg_resources.require(_PROJ_NAME)[0].version

FORMAT = '%(levelname)s: %(message)s'
_DIR = pathlib.Path(__file__).parent
PATH_TRANS_FEATURES_QUALIFIERS = _DIR / "translate_features_qualifiers.toml"

PATH_DDBJ_FILTER = _DIR / "ddbj_filter.toml"
PATH_METADATA_DEFAULT = _DIR / "metadata_without_COMMON.toml"

LOCUS_TAG_PREFIX = "LOCUSTAGPREFIX_"

IGNORE_FILTERING_RULES = False

# [NOTE] joined exons will be treated as mRNA locations
JOINABLES = ("CDS", "exon")

def main():
    parser = argparse.ArgumentParser(prog=_EXEC_NAME)
    parser.add_argument("--gff3", "--gff", metavar="FILE", help="Input GFF3 file")
    parser.add_argument("--fasta", metavar="FILE", help="Input FASTA file", required=True)
    parser.add_argument(
        "--metadata",
        help="Input metadata in TOML describing COMMON and other entires",
        metavar="FILE",
        default=PATH_METADATA_DEFAULT,
    )
    parser.add_argument(
        "-p",
        "--prefix",
        "--locus_tag_prefix",
        help="Prefix of locus_tag. See https://www.ddbj.nig.ac.jp/ddbj/locus_tag-e.html",
        metavar="STR",
        default=LOCUS_TAG_PREFIX,
    )
    parser.add_argument(
        "--transl_table",
        help="Genetic Code ID. 1 by default, and 11 for bacteria. See https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi",
        type=int,
        metavar="INT",
        default=1,
    )
    parser.add_argument(
        "--rename_setting",
        help="Rename setting for features and qualifiers",
        metavar="FILE",
        default=PATH_TRANS_FEATURES_QUALIFIERS,
    )
    parser.add_argument(
        "--filter_setting",
        help="A set of Feature-Qualifier pairs allowed in the output. See https://www.ddbj.nig.ac.jp/assets/files/pdf/ddbj/fq-e.pdf",
        metavar="FILE",
        default=PATH_DDBJ_FILTER,
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Specify annotation file name as output",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
        help="Show version",
    )
    parser.add_argument("--log", default=logging.INFO, help="[debug only] Set log level.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log, format=FORMAT)

    logging.info("Input GFF           : {}".format(args.gff3))
    logging.info("Input FASTA         : {}".format(args.fasta))
    logging.info("Input metadata      : {}".format(args.metadata))
    logging.info("Prefix of locus_tag : {}".format(args.prefix))
    logging.info("transl_table        : {}".format(args.transl_table))
    if args.rename_setting != PATH_TRANS_FEATURES_QUALIFIERS:
        logging.info(f"Rename setting      : {args.rename_setting}")
    if args.filter_setting != PATH_DDBJ_FILTER:
        logging.info(f"Filter setting      : {args.filter_setting}")
    output = args.output
    if output:
        logging.info("Output              : {}".format(output))

    metadata = utils.load_metadata_info(args.metadata)

    records = transforms.run(
        args.gff3,
        args.fasta,
        args.rename_setting,
        metadata,
        args.prefix,
        args.transl_table,
        joinables=JOINABLES,
    )

    logging.debug("Records: {}".format(records))

    fmt = formatter.DDBJFormatter(metadata, args.filter_setting)
    gen = fmt.run(records, ignore_rules=IGNORE_FILTERING_RULES)

    if output:
        parent_dir = pathlib.Path(output).parent
        parent_dir.mkdir(exist_ok=True)
        with open(output, "w") as f:
            for line in gen:
                print(line, file=f)
    else:
        for line in gen:
            print(line)


if __name__ == "__main__":
    main()
