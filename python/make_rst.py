#!/usr/bin/env python3
import argparse
import json
import jinja2


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generates source files based on a jinja2 template "
                    "and a json variable map")
    parser.add_argument(
        '-t', '--template', required=True,
        help='path to the jinja2 template file')
    parser.add_argument(
        '-m', '--map', required=True,
        help='path to the json variable map file')
    parser.add_argument(
        '-o', '--output', required=True,
        help='path to the output file')

    return parser.parse_args()


def read_template(path):
    with open(path, "r") as f:
        return jinja2.Template(f.read(), keep_trailing_newline=True)


def read_var_map(path):
    with open(path, "r") as f:
        return json.loads(f.read())


def main():
    args = parse_args()

    template = read_template(args.template)
    var_map = read_var_map(args.map)

    with open(args.output, "w") as f:
        f.write(template.render(var_map))


if __name__ == "__main__":
    main()
