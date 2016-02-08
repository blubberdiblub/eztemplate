#!/usr/bin/env python
"""Provide a simple templating system for text files."""

from __future__ import print_function

import argparse
import errno
import os
import os.path
import re
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
                       action='store_true',
                       dest='vary',
                       help="vary output file name according to template",
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
    group.add_argument('-c', '--concatenate',
                       action='store_true',
                       dest='concatenate',
                       help="concatenate multiple input files into one output",
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

    if args.vary:
        if len(args.outfiles) != 1:
            parser.error("need exactly one output file template")
        if hasattr(args.outfiles[0], 'write'):
            parser.error("vary required an output file template")
    elif not args.outfiles:
        args.outfiles = [sys.stdout]

    if not args.infiles:
        if args.args:
            infiles = args.remainder
            args.remainder = []
            try:
                infiles.remove('--')
            except ValueError:
                pass
        else:
            first = 1 if args.remainder and args.remainder[0] == '--' else 0
            last = (len(args.remainder)
                    if args.vary or args.concatenate
                    else first + 1)
            for split, infile in enumerate(args.remainder[first:last], first):
                if infile == '--' or '=' in infile:
                    break
            else:
                split = last

            infiles = args.remainder[first:split]
            args.remainder = args.remainder[split:]

        args.infiles = [path if path != '-' else sys.stdin
                        for path in infiles] if infiles else [sys.stdin]

    if args.args:
        flat_args = args.args
    else:
        flat_args = args.remainder
        args.remainder = []
        if flat_args and flat_args[0] == '--':
            flat_args = flat_args[1:]

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

    return ((outfile, infiles[0], arggroups[0]) for outfile in outfiles)


def variable_outfile_iterator(outfiles, infiles, arggroups, engine):
    """Iterate over variable output file name template."""
    assert len(outfiles) == 1

    template = engine(outfiles[0], tolerant=False)

    for infile in infiles:
        if infile is sys.stdin:
            path = '-'
        elif hasattr(infile, 'read'):
            try:
                path = infile.name
            except AttributeError:
                path = None
        else:
            path = infile

        if not path or infile is sys.stdin:
            dirname = basename = stem = ext = number = i = None
        else:
            dirname, basename = os.path.split(path)
            stem, ext = os.path.splitext(basename)
            number = re.findall(r'\d+', basename)
            i = number[-1] if number else None

        for arggroup in arggroups:
            mapping = dict(arggroup,
                           path=path,
                           dirname=dirname,
                           basename=basename,
                           stem=stem,
                           ext=ext,
                           number=number,
                           i=i,
                           )

            outfile = template.apply(mapping)

            yield (outfile, infile, arggroup)


def process_combinations(combinations, engine, tolerant=False):
    """Process outfile-infile-arggroup combinations."""
    outfiles = set()
    templates = {}

    for outfile, infile, arggroup in combinations:
        if infile in templates:
            template = templates[infile]
        else:
            if hasattr(infile, 'read'):
                template = infile.read()
                dirname = None
            else:
                with open(infile, 'r') as f:
                    template = f.read()
                dirname = os.path.dirname(infile)

            template = templates[infile] = engine(template,
                                                  dirname=dirname,
                                                  tolerant=tolerant)

        if outfile is sys.stdout:
            path = '-'
        elif hasattr(outfile, 'write'):
            try:
                path = outfile.name
            except AttributeError:
                path = None
        else:
            path = outfile

        if not path or outfile is sys.stdout:
            abspath = dirname = basename = stem = ext = realpath = None
            realdrive = realdir = realbase = realstem = realext = None
        else:
            abspath = os.path.abspath(path)

            dirname, basename = os.path.split(path)
            stem, ext = os.path.splitext(basename)

            if not dirname:
                dirname = os.curdir

            realpath = os.path.realpath(path)
            realdrive, tail = os.path.splitdrive(realpath)
            realdir, realbase = os.path.split(tail)
            realstem, realext = os.path.splitext(realbase)

        mapping = dict(arggroup,
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

        result = template.apply(mapping)

        if hasattr(outfile, 'write'):
            if result:
                outfile.write(result)
        elif result or not args.delete_empty:
            if outfile in outfiles:
                raise IOError("trying to write twice to the same file")
            outfiles.add(outfile)
            with open(outfile, 'w') as f:
                f.write(result)
        else:
            try:
                os.remove(outfile)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise


def main(args):
    """Main function."""
    engine = engines.engines[args.engine]

    if args.vary:
        it = variable_outfile_iterator(args.outfiles,
                                       args.infiles,
                                       args.args,
                                       engine)
    else:
        it = constant_outfile_iterator(args.outfiles,
                                       args.infiles,
                                       args.args)

    process_combinations(it, engine, tolerant=args.tolerant)


if __name__ == '__main__':
    args = parse_args()
    main(args)
