#-----------------------------------------------------------------------------
# Copyright (c) 2005-2020, PyInstaller Development Team.
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

# Third-party imports
# -------------------
import pytest

# Local imports
# -------------
from PyInstaller.utils.tests import importorskip
from PyInstaller.compat import exec_python_rc

# Directory with testing modules used in some tests.
_MODULES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'modules'
)


def __exec_python_script(script_filename, *args, pathex=None):
    cmd = [script_filename]
    cmd.extend(args)

    # Prepare the environment - default to 'os.environ'...
    env = copy.deepcopy(os.environ)
    # ... and prepend PYTHONPATH with pathex
    if pathex:
        if 'PYTHONPATH' in env:
            pathex = os.pathsep.join([pathex, env.get('PYTHONPATH')])
        env['PYTHONPATH'] = pathex

    return exec_python_rc(*cmd, env=env)


def __get_test_package_path(package_type):
    # Same test package, in three different formats
    if package_type == 'pkg':
        pathex = os.path.join(_MODULES_DIR,
                              'pyi_pkg_resources_provider',
                              'package')
    elif package_type == 'egg':
        pathex = os.path.join(_MODULES_DIR,
                              'pyi_pkg_resources_provider',
                              'egg-zipped.egg')

    return pathex


@importorskip('pkg_resources')
@pytest.mark.parametrize('package_type', ['pkg', 'egg'])
def test_pkg_resources_provider_source(package_type, script_dir):
    # Run the source python test script
    pathex = __get_test_package_path(package_type)
    test_script = 'pyi_pkg_resources_provider.py'

    # NOTE: str() is needed for python 3.5
    test_script = os.path.join(str(script_dir), test_script)
    ret = __exec_python_script(test_script, pathex=pathex)
    assert ret == 0, "Test script failed!"


@importorskip('pkg_resources')
@pytest.mark.parametrize('package_type', ['pkg', 'egg'])
def test_pkg_resources_provider_frozen(pyi_builder, package_type, script_dir):
    # Run the test script as a frozen program
    pathex = __get_test_package_path(package_type)
    test_script = 'pyi_pkg_resources_provider.py'

    hooks_dir = os.path.join(_MODULES_DIR,
                             'pyi_pkg_resources_provider',
                             'hooks')

    pyi_builder.test_script(test_script, pyi_args=[
        '--paths', pathex,
        '--hidden-import', 'pyi_pkgres_testpkg',
        '--additional-hooks-dir', hooks_dir]
    )
