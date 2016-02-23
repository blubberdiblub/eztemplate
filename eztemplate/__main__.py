#!/usr/bin/env python
"""Provide a simple templating system for text files."""

from __future__ import absolute_import
from __future__ import print_function

import argparse
import errno
import os
import os.path
import re
import sys

from . import engines
from . import __version__


def is_filelike(ob):
    """Check for filelikeness of an object.

    Needed to distinguish it from file names.
    Returns true if it has a read or a write method.
    """
    if hasattr(ob, 'read') and callable(ob.read):
        return True

    if hasattr(ob, 'write') and callable(ob.write):
        return True

    return False


class _PyArg(str):

    """Wrap a command line python argument.

    Makes it distinguishable from a plain text argument.
    """

    pass


def parse_args(args=None):
    """Parse command line arguments."""
    # The argparse module provides a nice abstraction for argument parsing.
    # It automatically builds up the help text, too.
    parser = argparse.ArgumentParser(
            prog=__package__,
            description='Make substitutions in text files.',
        )
    parser.add_argument('-V', '--version',
                        action='version',
                        version="%%(prog)s %s" % (__version__,),
                        )

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
    group.add_argument('-r', '--read-old',
                       action='store_true',
                       dest='read_old',
                       help="read preexisting output files and"
                            "hand the respective content to the template",
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
    group.add_argument('-p', '--pyarg',
                       action='append',
                       dest='args',
                       type=_PyArg,
                       help="evaluate a python expression",
                       metavar="NAME=EXPRESSION",
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
        if is_filelike(args.outfiles[0]):
            parser.error("vary requires an output file template")
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
        if isinstance(arg, _PyArg):
            name_value = arg.split('=', 1)
            mapping[name_value[0]] = eval(name_value[1], {}, mapping)
        elif arg == '--':
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


def make_path_properties(file_or_path, prefix=''):
    """Build useful properties from a file path."""
    is_std = file_or_path in (sys.stdin, sys.stdout, sys.stderr)

    if is_std:
        path = '-'
    elif is_filelike(file_or_path):
        try:
            path = str(file_or_path.name)
        except AttributeError:
            path = None
    else:
        path = str(file_or_path)

    if is_std or not path:
        abspath = dirname = basename = stem = ext = None
        realpath = realdrive = realdir = realbase = realstem = realext = None
        numbers = num = None
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

        numbers = [int(s) for s in re.findall(r'\d+', basename)]
        num = numbers[-1] if numbers else None

    return {
            prefix + 'path':      path,
            prefix + 'abspath':   abspath,
            prefix + 'dirname':   dirname,
            prefix + 'basename':  basename,
            prefix + 'stem':      stem,
            prefix + 'ext':       ext,
            prefix + 'realpath':  realpath,
            prefix + 'realdrive': realdrive,
            prefix + 'realdir':   realdir,
            prefix + 'realbase':  realbase,
            prefix + 'realstem':  realstem,
            prefix + 'realext':   realext,
            prefix + 'numbers':   numbers,
            prefix + 'num':       num,
        }


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
        properties = make_path_properties(infile, prefix='')

        for arggroup in arggroups:
            outfile = template.apply(dict(arggroup, **properties))
            yield (outfile, infile, arggroup)


class CachedTemplateReader(object):

    """Read templates and cache them."""

    def __init__(self, engine, tolerant=False):
        """Initialize reader."""
        self._engine = engine
        self._tolerant = tolerant
        self._cached_templates = {}

    def read(self, file_or_path):
        """Read template from cache or file."""
        if file_or_path in self._cached_templates:
            return self._cached_templates[file_or_path]

        if is_filelike(file_or_path):
            template = file_or_path.read()
            dirname = None
        else:
            with open(file_or_path, 'r') as f:
                template = f.read()
            dirname = os.path.dirname(file_or_path)

        template = self._engine(template,
                                dirname=dirname,
                                tolerant=self._tolerant)

        self._cached_templates[file_or_path] = template
        return template


def process_combinations(combinations, engine,
                         tolerant=False,
                         read_old=False,
                         delete_empty=False,
                         ):
    """Process outfile-infile-arggroup combinations."""
    outfiles = set()

    templatereader = CachedTemplateReader(engine, tolerant=tolerant)

    for outfile, infile, arggroup in combinations:
        template = templatereader.read(infile)
        properties = make_path_properties(outfile, prefix='ez_')

        if read_old:
            if is_filelike(outfile):
                raise Exception("cannot read already open output streams")
            try:
                with open(outfile, 'r') as f:
                    properties['ez_content'] = f.read()
            except IOError:
                properties['ez_content'] = None

        result = template.apply(dict(arggroup, **properties))

        if is_filelike(outfile):
            if result:
                outfile.write(result)
        elif result or not delete_empty:
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


def perform_templating(args):
    """Perform templating according to the given arguments."""
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

    process_combinations(it, engine,
                         tolerant=args.tolerant,
                         read_old=args.read_old,
                         delete_empty=args.delete_empty,
                         )


def main_command():
    """Parse command line arguments and perform main action."""
    args = parse_args()
    perform_templating(args)


if __name__ == '__main__':
    sys.exit(main_command())
