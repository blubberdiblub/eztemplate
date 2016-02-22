#!/usr/bin/env python

"""Setup for eztemplate."""

import errno
import os
import os.path
import pkgutil
import re
import subprocess

from setuptools import setup, find_packages


def get_version():
    """Build version number from git repository tag."""
    try:
        from eztemplate import version
    except ImportError:
        version = None

    try:
        git_version = subprocess.check_output(['git', 'describe', '--dirty'])
    except:
        if not version:
            raise ValueError("cannot determine version number")
        return version.__version__

    m = re.match(r'^\s*'
                 r'(?P<version>\S+?)'
                 r'(-(?P<post>\d+)-(?P<commit>g[0-9a-f]+))?'
                 r'(-(?P<dirty>dirty))?'
                 r'\s*$', git_version.decode())
    if not m:
        raise ValueError("cannot parse git describe output")

    git_version = m.group('version')
    post = m.group('post')
    commit = m.group('commit')
    dirty = m.group('dirty')

    local = []

    if post:
        post = int(post)
        if post:
            git_version += '.post%d' % (post,)
            if commit:
                local.append(commit)

    if dirty:
        local.append(dirty)

    if local:
        git_version += '+' + '.'.join(local)

    if not version or git_version != version.__version__:
        with open('eztemplate/version.py', 'w') as f:
            f.write("__version__ = %r\n" % (str(git_version),))

    return git_version


def get_long_description():
    """Provide README.md converted to reStructuredText format."""
    description = pkgutil.get_data(__name__, 'README.md')
    if description is None:
        return None

    try:
        process = subprocess.Popen([
                'pandoc',
                '-f', 'markdown_github',
                '-t', 'rst',
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return None
        raise

    description, __ = process.communicate(input=description)
    if process.poll() is None:
        process.kill()
        raise Exception("pandoc did not terminate")
    if process.poll():
        raise Exception("pandoc terminated abnormally")

    return description


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    setup(
            name='eztemplate',
            version=get_version(),
            author='Niels Boehm',
            author_email='blubberdiblub@gmail.com',
            description="Simple templating program to generate plain text"
                        " (like config files) from name-value pairs.",
            long_description=get_long_description(),
            license='MIT',
            keywords='templating text',
            url='https://github.com/blubberdiblub/eztemplate/',
            packages=find_packages(exclude=[
                    'tests',
                    'tests.*',
                    '*.tests',
                    '*.tests.*',
                ]),
            include_package_data=True,
            entry_points={
                'console_scripts': [
                    'eztemplate = eztemplate.__main__:main_command',
                ],
            }
        )
