#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# python-lxc: Python bindings for LXC
#
# (C) Copyright Canonical Ltd. 2012
#
# Authors:
# Stéphane Graber <stgraber@ubuntu.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import glob
import os
import subprocess

# Fix build when PIE is enabled (must run before setuptools import)
for var in ("LDFLAGS", "CFLAGS"):
    current = os.environ.get(var, None)
    if not current:
        continue

    new = []
    for flag in current.split(" "):
        if flag.lower() in ("-pie", "-fpie"):
            if "-fPIC" not in new:
                new.append("-fPIC")
            continue
        new.append(flag)

    os.environ[var] = " ".join(new)

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as BuildExtCommand


class LxcBuildExtCommand(BuildExtCommand):
    user_options = BuildExtCommand.user_options + [
        ('no-pkg-config', None,
         "don't use pkg-config to detect include/library paths")
    ]

    def initialize_options(self):
        super(LxcBuildExtCommand, self).initialize_options()
        self.no_pkg_config = False

    def build_extensions(self):
        if not self.no_pkg_config:
            pkg_config_executable = os.environ.get('PKG_CONFIG_EXECUTABLE',
                                                   'pkg-config')

            def get_pkg_config_var(name):
                args = [pkg_config_executable, '--variable', name, 'lxc']
                output = subprocess.check_output(args,
                                                 universal_newlines=True)
                return output.rstrip('\n')

            try:
                includedir = get_pkg_config_var('includedir')
                libdir = get_pkg_config_var('libdir')

                self.compiler.add_include_dir(includedir)
                self.compiler.add_library_dir(libdir)

            except subprocess.CalledProcessError:
                pass

        super(LxcBuildExtCommand, self).build_extensions()


setup(name='python3-lxc',
      version='3.0.1',
      description='Python3 bindings for LXC',
      long_description='The lxc-python3 package contains LXC bindings for python3',
      license='LGPLv2+',
      maintainer='lxc',
      maintainer_email='lxc-devel@lists.linuxcontainers.org',
      url='git://github.com/lxc/python3-lxc',
      packages=['lxc'],
      package_dir={'lxc': 'lxc'},
      ext_modules=[Extension('_lxc', sources=['lxc.c'], libraries=['lxc'])],
      cmdclass={'build_ext': LxcBuildExtCommand},
      )
