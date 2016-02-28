#!/usr/bin/env python

"""Setup for eztemplate."""

import ast
import errno
import os
import os.path
import re
import subprocess

from setuptools import setup, find_packages


def get_version():
    """Build version number from git repository tag."""
    try:
        f = open('eztemplate/version.py', 'r')
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise
        m = None
    else:
        m = re.match('^\s*__version__\s*=\s*(?P<version>.*)$', f.read(), re.M)
        f.close()

    __version__ = ast.literal_eval(m.group('version')) if m else None

    try:
        git_version = subprocess.check_output(['git', 'describe', '--dirty'])
    except:
        if __version__ is None:
            raise ValueError("cannot determine version number")
        return __version__

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

    if git_version != __version__:
        with open('eztemplate/version.py', 'w') as f:
            f.write("__version__ = %r\n" % (str(git_version),))

    return git_version


def get_long_description():
    """Provide README.md converted to reStructuredText format."""
    try:
        with open('README.md', 'r') as f:
            description = f.read()
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        return None

    try:
        process = subprocess.Popen([
                'pandoc',
                '-f', 'markdown_github',
                '-t', 'rst',
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            )
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
            keywords=[
                    'templating',
                    'text',
                ],
            url='https://github.com/blubberdiblub/eztemplate/',
            install_requires=[
                    'argparse',
                ],
            extras_require={
                    'empy': ['empy'],
                    'mako': ['mako'],
                },
            test_suite='tests',
            packages=find_packages(exclude=[
                    'tests',
                    'tests.*',
                    '*.tests',
                    '*.tests.*',
                ]),
            include_package_data=True,
            zip_safe=False,
            entry_points={
                'console_scripts': [
                    'eztemplate = eztemplate.__main__:main_command',
                ],
            },
            classifiers=[
                    'Development Status :: 4 - Beta',
                    'Environment :: Console',
                    'Intended Audience :: End Users/Desktop',
                    'Intended Audience :: System Administrators',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 3',
                    'Topic :: System :: Systems Administration',
                    'Topic :: Text Processing :: General',
                    'Topic :: Utilities',
                ],
        )
