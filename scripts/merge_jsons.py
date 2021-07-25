import utils.helper_functions as hf
import argparse
import json
import collections

target_directories = []
output_directory = "."

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="The directory or directories of the files that will be merged.", action="append")
    parser.add_argument("--output", help="The directory the output file is put in.")
    return parser.parse_args()


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


args = parse_args()

if args.target:
    target_directories = args.target

    output = {}

    for file in target_directories:
        with open(file, "r", encoding="utf-8-sig") as stream:
            data = json.load(stream)
            dict_merge(output, data)

    # write the output
    with open(output_directory, "w+", encoding="utf-8-sig") as stream:
        json.dump(stream, output)

else:
    print("Please input at least two target files.")