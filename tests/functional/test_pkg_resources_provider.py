# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

# Library imports
# ---------------
import copy
import os
import sys

# Third-party imports
# -------------------
import pytest
import py

# Local imports
# -------------
from PyInstaller.utils.tests import importorskip
from PyInstaller.compat import exec_python_rc

# :todo: find a way to get this from `conftest` or such
# Directory with testing modules used in some tests.
_MODULES_DIR = py.path.local(os.path.abspath(__file__)).dirpath('modules')

def __exec_python_script(script_filename, *args, pathex=None):
    cmd = [script_filename]
    cmd.extend(args)

    # Prepare the environment - default to 'os.environ'...
    env = copy.deepcopy(os.environ)
    # ... and prepend PYTHONPATH with pathex
    if pathex:
        if 'PYTHONPATH' in env:
            pathex = os.pathsep.join([env.get('PYTHONPATH'), pathex])
        env['PYTHONPATH'] = pathex

    return exec_python_rc(*cmd, env=env)

def __get_test_module_path(module_type):
    # Same test module, in three different formats
    if module_type == 'module':
        pathex = os.path.join(_MODULES_DIR,
                              'pyi-pkg-resources-test-modules',
                              'module')
    elif module_type == 'egg':
        pathex = os.path.join(_MODULES_DIR,
                              'pyi-pkg-resources-test-modules',
                              'egg-zipped.egg')

    return pathex

@importorskip('pkg_resources')
@pytest.mark.parametrize('module_type', ['module', 'egg'])
def test_pkg_resources_provider_source(module_type, script_dir):
    # Run the source python test script
    pathex = __get_test_module_path(module_type)
    test_script = 'pyi_pkg_resources_provider.py'

    test_script = os.path.join(script_dir, test_script)
    ret = __exec_python_script(test_script, pathex=pathex)
    assert ret == 0, "Test script failed!"

@importorskip('pkg_resources')
@pytest.mark.parametrize('module_type', ['module', 'egg'])
def test_pkg_resources_provider_frozen(pyi_builder, module_type, script_dir):
    # Run the test script as a frozen program
    pathex = __get_test_module_path(module_type)
    test_script = 'pyi_pkg_resources_provider.py'

    hooks_dir = os.path.join(_MODULES_DIR,
                             'pyi-pkg-resources-test-modules',
                             'hooks')

    pyi_builder.test_script(test_script, pyi_args=[
        '--paths', pathex,
        '--hidden-import', 'pyi_pkgres_testmod',
        '--additional-hooks-dir', hooks_dir]
    )
