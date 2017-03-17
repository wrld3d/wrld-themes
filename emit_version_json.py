import argparse
import json
import os
import sys


def main(inputs, output_path, store_path):
    results = {}
    for i in inputs:
        name, _ = os.path.splitext(os.path.basename(i))
        results[name] = "{}/{}/".format(store_path, name)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write version information about a theme build to a json file")
    parser.add_argument("--store_path", "-s", help="The store path that manifests were written to", required=True)
    parser.add_argument("--output", "-o", help="Path to output json to", required=True)
    parser.add_argument("inputs", help="Manifest roots used in this build", nargs="+")
    args = parser.parse_args()

    main(args.inputs, args.output, args.store_path)