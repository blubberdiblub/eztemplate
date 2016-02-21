#!/usr/bin/env python

"""Setup for eztemplate."""

import os
import os.path
import re
import subprocess

from setuptools import setup


def get_version():
    """Build version number from git repository tag."""
    version = subprocess.check_output(['git', 'describe', '--dirty']).decode()
    m = re.match(r'^\s*'
                 r'(?P<version>\S+?)'
                 r'(-(?P<post>\d+)-(?P<commit>g[0-9a-f]+))?'
                 r'(-(?P<dirty>dirty))?'
                 r'\s*$', version)
    if not m:
        raise ValueError("cannot parse git describe output")

    version = m.group('version')
    post = m.group('post')
    commit = m.group('commit')
    dirty = m.group('dirty')

    local = []

    if post:
        post = int(post)
        if post:
            version += '.post%d' % (post,)
            if commit:
                local.append(commit)

    if dirty:
        local.append(dirty)

    if local:
        version += '+' + '.'.join(local)

    return version


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    setup(
            name='eztemplate',
            version=get_version(),
            author='Niels Boehm',
            author_email='blubberdiblub@gmail.com',
            description="Simple templating program to generate plain text"
                        " (like config files) from name-value pairs.",
            license='MIT',
            keywords='templating text',
            url='https://github.com/blubberdiblub/eztemplate/',
            py_modules=['eztemplate'],
            packages=[
                'engines',
                'tests',
            ],
            include_package_data=True,
            entry_points={
                'console_scripts': [
                    'eztemplate = eztemplate:main_command',
                ],
            }
        )
