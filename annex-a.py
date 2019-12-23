#!/usr/bin/env python
import argparse
from fddc.config import Config
from fddc.annex_a.merger import merge

def main():
    parser = argparse.ArgumentParser(description='Merge and convert Annex A files')

    parser.add_argument('--mergefile', type=str, nargs='+', required=False,
                        help='The filename or pattern to scan')

    parser.add_argument('--mergeoutput', type=str, default="merged.xlsx", required=False,
                        help='The output of the merge process')

    parser.add_argument('--config', '-c', type=str, nargs='+', required=False,
                        help='Additional config files')

    args = parser.parse_args()

    config = Config("config/merge-datasources.yml", *args.config)
    config.update(**args)

    # if args.mergefile is not None:
    #     config["input_files"] = args.mergefile
    #
    # if args.mergeoutput is not None:
    #     config["output_file"] = args.mergeoutput

    merge(config)


main()

