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

# A test script for validation of pkg_resources provider implementation.
#
# The test module/package has the following structure:
#
# pyi_pkgres_testmod
# ├── __init__.py
# └── submod
#     ├── data
#     │   ├── entry1.txt
#     │   ├── entry2.txt
#     │   ├── entry3.txt
#     │   └── extra
#     │       └── extra_entry1.txt
#     └── __init__.py

# When run as native python script, this script can be used to check the
# behavior of "native" providers that come with pkg_resources, e.g.,
# DefaultProvider (for regular modules/packages) and ZipProvider (for
# eggs).
#
# When run as a frozen application, this script validates the behavior
# of the frozen provider implemented by PyInstaller. Due to transitivity
# of test results, this script running without errors both as a native
# script and as a frozen application serves as proof of conformance for
# the PyInstaller's provider.
#
# Wherever the behavior between the native providers is inconsistent,
# we allow the same leeway for the PyInstaller's frozen provider.

import sys
from pkg_resources import resource_exists, resource_isdir, resource_listdir
from pkg_resources import get_provider, DefaultProvider, ZipProvider

modname = 'pyi_pkgres_testmod'

# Identify provider type
provider = get_provider(modname)
is_default = isinstance(provider, DefaultProvider)
is_zip = isinstance(provider, ZipProvider)
is_frozen = getattr(sys, 'frozen', False)

assert any([is_default, is_zip, is_frozen]), "Unsupported provider type!"


########################################################################
#                Validate behavior of resource_exists()                #
########################################################################
# Module's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_exists(modname, '.')
assert (is_default and ret == True) or \
       (is_zip and ret == False)

# Submodule's directory (relative to module):
#  * both DefaultProvider and ZipProvider return True
assert resource_exists(modname, 'submod') == True

# Submodule directory (relative to submodule):
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_exists(modname + '.submod', '.')
assert (is_default and ret == True) or \
       (is_zip and ret == False)

# Data directory in submodule
assert resource_exists(modname, 'submod/data') == True
assert resource_exists(modname + '.submod', 'data') == True

# Subdirectory in data directory
assert resource_exists(modname, 'submod/data/extra') == True
assert resource_exists(modname + '.submod', 'data/extra') == True

# Subdirectory in data directory (invalid module name)
#  * DefaultProvider raises TypeError
#  * ZipProvider raises ModuleNotFoundError
try:
    resource_exists(modname + '.submod.data', 'extra')
except TypeError:
    assert is_default
except ModuleNotFoundError:
    assert is_zip
except:
    raise
else:
    assert False

# File in data directory
assert resource_exists(modname, 'submod/data/entry1.txt') == True

# Deeply nested data file
assert resource_exists(modname, 'submod/data/extra/extra_entry1.txt') == True

# A non-existant file/directory - should return False
assert resource_exists(modname, 'submod/non-existant') == False

# A source script file in top-level module
assert resource_exists(modname, '__init__.py') == True

# Parent of module's top-level directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_exists(modname, '..')
assert (is_default and ret == True) or \
       (is_zip and ret == False)

# Parent of submodule
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_exists(modname + '.submod', '..')
assert (is_default and ret == True) or \
       (is_zip and ret == False)


########################################################################
#                Validate behavior of resource_isdir()                 #
########################################################################
# Module's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_isdir(modname, '.')
assert (is_default and ret == True) or \
       (is_zip and ret == False)

# Submodule's directory (relative to module):
#  * both DefaultProvider and ZipProvider return True
assert resource_isdir(modname, 'submod') == True

# Submodule directory (relative to submodule):
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_isdir(modname + '.submod', '.')
assert (is_default and ret == True) or \
       (is_zip and ret == False)

# Data directory in submodule
assert resource_isdir(modname, 'submod/data') == True
assert resource_isdir(modname + '.submod', 'data') == True

# Subdirectory in data directory
assert resource_isdir(modname, 'submod/data/extra') == True
assert resource_isdir(modname + '.submod', 'data/extra') == True

# Subdirectory in data directory (invalid module name)
#  * DefaultProvider raises TypeError
#  * ZipProvider raises ModuleNotFoundError
try:
    resource_isdir(modname + '.submod.data', 'extra')
except TypeError:
    assert is_default
except ModuleNotFoundError:
    assert is_zip
except:
    raise
else:
    assert False

# File in data directory - should return False
assert resource_isdir(modname, 'submod/data/entry1.txt') == False

# Deeply nested data file - should return False
assert resource_isdir(modname, 'submod/data/extra/extra_entry1.txt') == False

# A non-existant file-directory - should return False
assert resource_isdir(modname, 'submod/non-existant') == False

# A source script file in top-level module - should return False
assert resource_isdir(modname, '__init__.py') == False

# Parent of module's top-level directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_isdir(modname, '..')
assert (is_default and ret == True) or \
       (is_zip and ret == False)

# Parent of submodule
#  * DefaultProvider returns True
#  * ZipProvider returns False
ret = resource_isdir(modname + '.submod', '..')
assert (is_default and ret == True) or \
       (is_zip and ret == False)


########################################################################
#               Validate behavior of resource_listdir()                #
########################################################################
# List module's top-level directory
#  * DefaultProvider lists the directory
#  * ZipProvider returns empty list
expected = {'__init__.py', 'submod'}

content = resource_listdir(modname, '.')
content = set(content)

if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__

assert (is_default and content == expected) or \
       (is_zip and content == set())

# List submodule directory
expected = {'__init__.py', 'data'}

content = resource_listdir(modname, 'submod')
content = set(content)

if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__

assert content == expected

# List data directory in submodule (relative to module)
expected = {'entry1.txt', 'entry2.txt', 'entry3.txt', 'extra'}

content = resource_listdir(modname, 'submod/data')
content = set(content)

assert content == expected

# List data directory in submodule (relative to submodule)
content = resource_listdir(modname + '.submod', 'data')
content = set(content)

assert content == expected

# List data in subdirectory of data directory in submodule
expected = {'extra_entry1.txt'}

content = resource_listdir(modname + '.submod', 'data/extra')
content = set(content)

assert content == expected


# Attempt to list a file (existing resource but not a directory).
#  * DefaultProvider raises NotADirectoryError
#  * ZipProvider returns empty list
try:
    content = resource_listdir(modname + '.submod', 'data/entry1.txt')
except NotADirectoryError:
    assert is_default
except:
    raise
else:
    assert is_zip and content == []


# Attempt to list an non-existant directory in main module.
#  * DefaultProvider raises FileNotFoundError
#  * ZipProvider returns empty list
try:
    content = resource_listdir(modname, 'non-existant')
except FileNotFoundError:
    assert is_default
except:
    raise
else:
    assert is_zip and content == []

# Attempt to list an non-existant directory in submodule
#  * DefaultProvider raises FileNotFoundError
#  * ZipProvider returns empty list
try:
    content = resource_listdir(modname + '.submod', 'data/non-existant')
except FileNotFoundError:
    assert is_default
except:
    raise
else:
    assert is_zip and content == []


# Attempt to list module's parent
#  * DefaultProvider actually lists the parent directory
#  * ZipProvider returns empty list
content = resource_listdir(modname, '..')
content = set(content)

assert (is_default and modname in content) or \
       (is_zip and content == set())

# Attempt to list submodule's parent
#  * DefaultProvider actually lists the parent directory
#  * ZipProvider returns empty list
expected = {'__init__.py', 'submod'}

content = resource_listdir(modname + '.submod', '..')
content = set(content)

if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__

assert (is_default and content == expected) or \
       (is_zip and content == set())
