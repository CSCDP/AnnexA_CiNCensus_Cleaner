#!/usr/bin/env python
import argparse
import logging
from fddc.config import Config
from fddc.annex_a.merger import merge


def main():
    parser = argparse.ArgumentParser(description='Merge and convert Annex A files')

    parser.add_argument('-f', '--input_files', metavar='file', type=str, nargs='+', required=False,
                        help='The filename or pattern to scan')

    parser.add_argument('-o', '--output_file', type=str, default="merged.xlsx", required=False,
                        help='The output of the merge process')

    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Verbose logging')

    parser.add_argument('--config', '-c', type=str, nargs='+', required=False, default=[],
                        help='Additional config files')

    args = parser.parse_args()

    config_args = {k: v for k, v in vars(args).items() if v is not None}

    config = Config("config/annex_a_merge.yml", *args.config)
    config.update(**config_args)

    level = logging.DEBUG if args.verbose > 0 else logging.INFO

    logging.basicConfig(level=level, format='%(asctime)-15s [%(module)s] %(message)s')

    merge(config)


main()
