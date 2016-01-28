#!/usr/bin/env python3
"""Provide a simple templating system for text files."""

from __future__ import print_function

import argparse
import sys

import engines


def argument_parser():
    """Parse command line arguments GNU style."""
    # The argparse module provides a nice abstraction for argument parsing.
    # It automatically builds up the help text, too.
    parser = argparse.ArgumentParser(
            description='Make substitutions in text files.')

    parser.add_argument('-e', '--engine',
                        help='templating engine',
                        dest='engine',
                        default='string.Template',
                        )
    parser.add_argument('-t', '--tolerant',
                        action='store_true',
                        help="don't fail on missing names",
                        dest='tolerant',
                        )
    parser.add_argument('-o', '--outfile',
                        help='output file',
                        dest='outfile',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        )
    parser.add_argument('-a', '--arg',
                        help='any number of name-value-pairs',
                        action='append',
                        dest='arg',
                        )
    parser.add_argument('file',
                        help='files to process',
                        nargs='*',
                        type=argparse.FileType('r'),
                        default=[sys.stdin],
                        )

    return parser


def dump_engines(target=sys.stderr):
    """Print successfully imported templating engines."""
    print("Available templating engines:", file=target)

    width = max(len(engine) for engine in engines.engines)
    for handle, engine in sorted(engines.engines.items()):
        description = engine.__doc__.split('\n', 0)[0]
        print("  %-*s  -  %s" % (width, handle, description), file=target)


def check_engine(handle):
    """Check availability of requested template engine."""
    if handle == 'help':
        dump_engines()
        sys.exit(0)

    if handle not in engines.engines:
        print('Engine "%s" is not available.' % (handle,), file=sys.stderr)
        sys.exit(1)


def make_mapping(args):
    """Make a mapping from the name=value pairs."""
    mapping = {}

    if args:
        for arg in args:
            name_value = arg.split('=', 1)
            mapping[name_value[0]] = (name_value[1]
                                      if len(name_value) > 1
                                      else None)

    return mapping


def main(args):
    """Main function."""
    check_engine(args.engine)
    engine = engines.engines[args.engine]
    mapping = make_mapping(args.arg)

    for f in args.file:
        raw_template = f.read()
        template = engine(raw_template, tolerant=args.tolerant)
        args.outfile.write(template.apply(mapping))


if __name__ == '__main__':
    parser = argument_parser()
    args = parser.parse_args()
    main(args)
