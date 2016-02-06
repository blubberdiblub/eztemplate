#!/usr/bin/env python
"""Provide a simple templating system for text files."""

from __future__ import print_function

import argparse
import os
import os.path
import sys

import engines


def parse_args(args=None):
    """Parse command line arguments."""
    # The argparse module provides a nice abstraction for argument parsing.
    # It automatically builds up the help text, too.
    parser = argparse.ArgumentParser(
            description='Make substitutions in text files.')

    group = parser.add_argument_group("Engine")
    group.add_argument('-e', '--engine',
                       dest='engine',
                       default='string.Template',
                       help="templating engine",
                       metavar="ENGINE",
                       )
    group.add_argument('-t', '--tolerant',
                       action='store_true',
                       dest='tolerant',
                       help="don't fail on missing names",
                       )

    group = parser.add_argument_group("Output")
    group.add_argument('-s', '--stdout',
                       action='append_const',
                       dest='outfiles',
                       const=sys.stdout,
                       help="use standard output",
                       )
    group.add_argument('-o', '--outfile',
                       action='append',
                       dest='outfiles',
                       help="output file",
                       metavar="FILE",
                       )
    group.add_argument('--vary',
                       dest='vary',
                       help="vary output file name according to template",
                       metavar="TEMPLATE",
                       )
    group.add_argument('-d', '--delete-empty',
                       action='store_true',
                       dest='delete_empty',
                       help="delete file if output is empty",
                       )

    group = parser.add_argument_group("Input")
    group.add_argument('--stdin',
                       action='append_const',
                       dest='infiles',
                       const=sys.stdin,
                       help="use standard input",
                       )
    group.add_argument('-i', '--infile',
                       action='append',
                       dest='infiles',
                       help="any number of input files",
                       metavar="FILE",
                       )

    group = parser.add_argument_group("Name-value pairs")
    group.add_argument('-a', '--arg',
                       action='append',
                       dest='args',
                       help="any number of name-value pairs",
                       metavar="NAME=VALUE",
                       )
    group.add_argument('-n', '--next',
                       action='append_const',
                       dest='args',
                       const='--',
                       help="begin next argument group",
                       )

    parser.add_argument(
                        dest='remainder',
                        nargs=argparse.REMAINDER,
                        help="possible input files and name-value pair groups "
                             "if not already specified through options",
                        )

    args = parser.parse_args(args)

    if args.engine == 'help':
        dump_engines()
        parser.exit(0)

    if args.engine not in engines.engines:
        parser.error("Engine '%s' is not available." % (args.engine,))

    if args.outfiles and args.vary:
        parser.error("cannot use both static and varying output files")
    elif not args.outfiles and not args.vary:
        args.outfiles = [sys.stdout]

    if not args.infiles:
        if args.args:
            i = len(args.remainder)
        else:
            try:
                i = args.remainder.index('--')
            except ValueError:
                i = len(args.remainder)

        args.infiles = [name if name != '-' else sys.stdin
                        for name in args.remainder[:i]] if i else [sys.stdin]
        args.remainder = args.remainder[i + 1:]

    if args.args:
        flat_args = args.args
    else:
        flat_args = args.remainder
        args.remainder = []

    args.args = []
    mapping = {}
    for arg in flat_args:
        if arg == '--':
            args.args.append(mapping)
            mapping = {}
        else:
            name_value = arg.split('=', 1)
            mapping[name_value[0]] = (name_value[1]
                                      if len(name_value) > 1
                                      else None)
    args.args.append(mapping)

    if args.remainder:
        parser.error("extraneous arguments left over")
    else:
        del args.remainder

    return args


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


def constant_outfile_iterator(outfiles, infiles, arggroups):
    """Iterate over all output files."""
    assert len(infiles) == 1
    assert len(arggroups) == 1

    for outfile in outfiles:
        if outfile is sys.stdout:
            path = '-'
        elif hasattr(outfile, 'write'):
            try:
                path = outfile.name
            except AttributeError:
                path = None
        else:
            path = outfile

        abspath = os.path.abspath(path)

        dirname, basename = os.path.split(path)
        stem, ext = os.path.splitext(basename)

        realpath = os.path.realpath(path)
        realdrive, tail = os.path.splitdrive(realpath)
        realdir, realbase = os.path.split(tail)
        realstem, realext = os.path.splitext(realbase)

        mapping = dict(arggroups[0],
                       ez_path=path,
                       ez_abspath=abspath,
                       ez_dirname=dirname,
                       ez_basename=basename,
                       ez_stem=stem,
                       ez_ext=ext,
                       ez_realpath=realpath,
                       ez_realdrive=realdrive,
                       ez_realdir=realdir,
                       ez_realbase=realbase,
                       ez_realstem=realstem,
                       ez_realext=realext,
                       )

        yield (outfile, infiles[0], mapping)


def main(args):
    """Main function."""
    engine = engines.engines[args.engine]

    if args.vary:
        raise NotImplementedError("vary is not yet implemented")
    else:
        it = constant_outfile_iterator(args.outfiles,
                                       args.infiles,
                                       args.args)

    for outfile, infile, mapping in it:
        if hasattr(infile, 'read'):
            raw_template = infile.read()
            dirname = None
        else:
            with open(infile, 'r') as f:
                raw_template = f.read()
            dirname = os.path.dirname(infile)

        template = engine(raw_template,
                          dirname=dirname,
                          tolerant=args.tolerant)

        result = template.apply(mapping)

        if hasattr(outfile, 'write'):
            if result:
                outfile.write(result)
        elif result or not args.delete_empty:
            with open(outfile, 'w') as f:
                f.write(result)
        else:
            os.remove(outfile)


if __name__ == '__main__':
    args = parse_args()
    main(args)
