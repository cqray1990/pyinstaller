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
#
# A test script for validation of pkg_resources provider implementation.
#
# The test package has the following structure:
#
# pyi_pkgres_testpkg/
# ├── a.py
# ├── b.py
# ├── __init__.py
# ├── subpkg1
# │   ├── c.py
# │   ├── data
# │   │   ├── entry1.txt
# │   │   ├── entry2.txt
# │   │   ├── entry3.txt
# │   │   └── extra
# │   │       └── extra_entry1.txt
# │   ├── d.py
# │   └── __init__.py
# ├── subpkg2
# │   ├── __init__.py
# │   ├── mod.py
# │   └── subsubpkg21
# │       ├── __init__.py
# │       └── mod.py
# └── subpkg3
#     ├── _datafile.txt
#     └── __init__.py
#
# When run as unfrozen script, this script can be used to check the
# behavior of "native" providers that come with pkg_resources, e.g.,
# DefaultProvider (for regular packages) and ZipProvider (for eggs).
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

pkgname = 'pyi_pkgres_testpkg'

# Identify provider type
provider = get_provider(pkgname)
is_default = isinstance(provider, DefaultProvider)
is_zip = isinstance(provider, ZipProvider)
is_frozen = getattr(sys, 'frozen', False)

assert is_default or is_zip or is_frozen, "Unsupported provider type!"

########################################################################
#                Validate behavior of resource_exists()                #
########################################################################
# Package's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider returns True
ret = resource_exists(pkgname, '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Package's directory, with empty path
assert resource_exists(pkgname, '') is True

# Subpackage's directory (relative to main package):
assert resource_exists(pkgname, 'subpkg1') is True
assert resource_exists(pkgname, 'subpkg2') is True
assert resource_exists(pkgname, 'subpkg2/subsubpkg21') is True
assert resource_exists(pkgname, 'subpkg3') is True

# Subpackage's directory (relative to subpackage itself):
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider returns True
ret = resource_exists(pkgname + '.subpkg1', '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Subpackage's directory (relative to subpackage itself), with empty path:
assert resource_exists(pkgname + '.subpkg1', '') is True

# Data directory in subpackage
assert resource_exists(pkgname, 'subpkg1/data') is True
assert resource_exists(pkgname + '.subpkg1', 'data') is True

# Subdirectory in data directory
assert resource_exists(pkgname, 'subpkg1/data/extra') is True
assert resource_exists(pkgname + '.subpkg1', 'data/extra') is True

# File in data directory
assert resource_exists(pkgname, 'subpkg1/data/entry1.txt') is True

# Deeply nested data file
assert resource_exists(pkgname, 'subpkg1/data/extra/extra_entry1.txt') is True

# A non-existant file/directory - should return False
assert resource_exists(pkgname, 'subpkg1/non-existant') is False

# A source script file in package
#  > PyiFrozenProvider returns False because frozen application does
#    not contain source files
ret = resource_exists(pkgname, '__init__.py')
assert (not is_frozen and ret is True) or \
       (is_frozen and ret is False)

# Parent of pacakge's top-level directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider disallows jumping to parent, and returns False
# NOTE: using .. in path is deprecated (since setuptools 40.8.0) and
# will raise exception in a future release
ret = resource_exists(pkgname, '..')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is False)

# Parent of subpackage's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider disallows jumping to parent, and returns False
# NOTE: using .. in path is deprecated (since setuptools 40.8.0) and
# will raise exception in a future release
ret = resource_exists(pkgname + '.subpkg1', '..')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is False)

# Submodule in main package
ret = resource_exists(pkgname + '.a', '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Submodule in main package, with empty path
assert resource_exists(pkgname + '.a', '') is True

# Submodule in subpackage
ret = resource_exists(pkgname + '.subpkg1.c', '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Submodule in subpackage, with empty path
assert resource_exists(pkgname + '.subpkg1.c', '') is True

########################################################################
#                Validate behavior of resource_isdir()                 #
########################################################################
# Package's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider returns True
ret = resource_isdir(pkgname, '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Package's directory, with empty path
assert resource_isdir(pkgname, '') is True

# Subpackage's directory (relative to main pacakge):
#  * both DefaultProvider and ZipProvider return True
assert resource_isdir(pkgname, 'subpkg1') is True
assert resource_isdir(pkgname, 'subpkg2') is True
assert resource_isdir(pkgname, 'subpkg2/subsubpkg21') is True
assert resource_isdir(pkgname, 'subpkg3') is True

# Subpackage's directory (relative to subpackage itself):
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider returns True
ret = resource_isdir(pkgname + '.subpkg1', '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Subpackage's directory (relative to subpackage itself), with empty path:
assert resource_isdir(pkgname + '.subpkg1', '') is True

# Data directory in subpackage
assert resource_isdir(pkgname, 'subpkg1/data') is True
assert resource_isdir(pkgname + '.subpkg1', 'data') is True

# Subdirectory in data directory
assert resource_isdir(pkgname, 'subpkg1/data/extra') is True
assert resource_isdir(pkgname + '.subpkg1', 'data/extra') is True

# File in data directory - should return False
assert resource_isdir(pkgname, 'subpkg1/data/entry1.txt') is False

# Deeply nested data file - should return False
assert resource_isdir(pkgname, 'subpkg1/data/extra/extra_entry1.txt') is False

# A non-existant file-directory - should return False
assert resource_isdir(pkgname, 'subpkg1/non-existant') is False

# A source script file in package - should return False
# NOTE: PyFrozenProvider returns False because the file does not
# exist.
assert resource_isdir(pkgname, '__init__.py') is False

# Parent of package's top-level directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider disallows jumping to parent, and returns False
# NOTE: using .. in path is deprecated (since setuptools 40.8.0) and
# will raise exception in a future release
ret = resource_isdir(pkgname, '..')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is False)

# Parent of subpacakge's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
#  > PyiFrozenProvider disallows jumping to parent, and returns False
# NOTE: using .. in path is deprecated (since setuptools 40.8.0) and
# will raise exception in a future release
ret = resource_isdir(pkgname + '.subpkg1', '..')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is False)

# Submodule in main package
ret = resource_isdir(pkgname + '.a', '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Submodule in main package, with empty path
assert resource_isdir(pkgname + '.a', '') is True

# Submodule in subpackage
ret = resource_isdir(pkgname + '.subpkg1.c', '.')
assert (is_default and ret is True) or \
       (is_zip and ret is False) or \
       (is_frozen and ret is True)

# Submodule in subpackage, with empty path
assert resource_isdir(pkgname + '.subpkg1.c', '') is True

########################################################################
#               Validate behavior of resource_listdir()                #
########################################################################
# List package's top-level directory
#  * DefaultProvider lists the directory
#  * ZipProvider returns empty list
#  > PyiFrozenProvider lists the directory, but does not provide source
#    .py files
expected = {'__init__.py', 'a.py', 'b.py', 'subpkg1', 'subpkg2', 'subpkg3'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname, '.')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert (is_default and content == expected) or \
       (is_zip and content == set()) or \
       (is_frozen and content == expected)

# List package's top-level directory, with empty path
#  > PyiFrozenProvider lists the directory, but does not provide source
#    .py files
expected = {'__init__.py', 'a.py', 'b.py', 'subpkg1', 'subpkg2', 'subpkg3'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname, '')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# List subpackage's directory (relative to main package)
#  > PyiFrozenProvider lists the directory, but does not provide source
#    .py files
expected = {'__init__.py', 'c.py', 'd.py', 'data'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname, 'subpkg1')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# List data directory in subpackage (relative to main package)
expected = {'entry1.txt', 'entry2.txt', 'entry3.txt', 'extra'}
content = resource_listdir(pkgname, 'subpkg1/data')
content = set(content)
assert content == expected

# List data directory in subpackage (relative to subpackage itself)
content = resource_listdir(pkgname + '.subpkg1', 'data')
content = set(content)
assert content == expected

# List data in subdirectory of data directory in subpackage
expected = {'extra_entry1.txt'}
content = resource_listdir(pkgname + '.subpkg1', 'data/extra')
content = set(content)
assert content == expected

# Attempt to list a file (existing resource but not a directory).
#  * DefaultProvider raises NotADirectoryError
#  * ZipProvider returns empty list
#  > PyiFrozenProvider returns empty list
try:
    content = resource_listdir(pkgname + '.subpkg1', 'data/entry1.txt')
except NotADirectoryError:
    assert is_default
except Exception:
    raise
else:
    assert (is_zip or is_frozen) and content == []

# Attempt to list an non-existant directory in main package.
#  * DefaultProvider raises FileNotFoundError
#  * ZipProvider returns empty list
#  > PyiFrozenProvider returns empty list
try:
    content = resource_listdir(pkgname, 'non-existant')
except FileNotFoundError:
    assert is_default
except Exception:
    raise
else:
    assert (is_zip or is_frozen) and content == []

# Attempt to list an non-existant directory in subpackage
#  * DefaultProvider raises FileNotFoundError
#  * ZipProvider returns empty list
#  > PyiFrozenProvider returns empty list
try:
    content = resource_listdir(pkgname + '.subpkg1', 'data/non-existant')
except FileNotFoundError:
    assert is_default
except Exception:
    raise
else:
    assert (is_zip or is_frozen) and content == []

# Attempt to list pacakge's parent directory
#  * DefaultProvider actually lists the parent directory
#  * ZipProvider returns empty list
#  > PyiFrozenProvider disallows jumping to parent, and returns empty list
# NOTE: using .. in path is deprecated (since setuptools 40.8.0) and
# will raise exception in a future release
content = resource_listdir(pkgname, '..')
assert (is_default and pkgname in content) or \
       (is_zip and content == []) or \
       (is_frozen and content == [])

# Attempt to list subpackage's parent directory
#  * DefaultProvider actually lists the parent directory
#  * ZipProvider returns empty list
#  > PyiFrozenProvider disallows jumping to parent, and returns False
# NOTE: using .. in path is deprecated (since setuptools 40.8.0) and
# will raise exception in a future release
expected = {'__init__.py', 'a.py', 'b.py', 'subpkg1', 'subpkg2', 'subpkg3'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname + '.subpkg1', '..')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert (is_default and content == expected) or \
       (is_zip and content == set()) or \
       (is_frozen and content == set())

# Attempt to list directory of subpackage that has no data files or
# directories (relative to main package)
expected = {'__init__.py', 'mod.py', 'subsubpkg21'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname, 'subpkg2')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# Attempt to list directory of subpackage that has no data files or
# directories (relative to subpackage itself)
expected = {'__init__.py', 'mod.py', 'subsubpkg21'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname + '.subpkg2', '')  # empty path!
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# Attempt to list directory of subsubpackage that has no data
# files/directories (relative to main package)
expected = {'__init__.py', 'mod.py'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname, 'subpkg2/subsubpkg21')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# Attempt to list directory of subsubpackage that has no data
# files/directories (relative to parent subpackage)
expected = {'__init__.py', 'mod.py'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname + '.subpkg2', 'subsubpkg21')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# Attempt to list directory of subsubpackage that has no data
# files/directories (relative to subsubpackage itself)
expected = {'__init__.py', 'mod.py'}
if is_frozen:
    expected = {x for x in expected if not x.endswith('.py')}
content = resource_listdir(pkgname + '.subpkg2.subsubpkg21', '')  # empty path!
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected

# Attempt to list submodule in main package - should give the same results
# as listing the package itself
assert set(resource_listdir(pkgname + '.a', '')) == \
       set(resource_listdir(pkgname, ''))  # empty path!

# Attempt to list submodule in subpackage - should give the same results
# as listing the subpackage itself
assert set(resource_listdir(pkgname + '.subpkg1.c', '')) == \
       set(resource_listdir(pkgname + '.subpkg1', ''))  # empty path!
