#-----------------------------------------------------------------------------
# Copyright (c) 2014-2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------


"""
Utils for Mac OS X platform.
"""

import os
import shutil
import pathlib
import fnmatch

from ..compat import base_prefix
from macholib.MachO import MachO


def is_homebrew_env():
    """
    Check if Python interpreter was installed via Homebrew command 'brew'.

    :return: True if Homebrew else otherwise.
    """
    # Python path prefix should start with Homebrew prefix.
    env_prefix = get_homebrew_prefix()
    if env_prefix and base_prefix.startswith(env_prefix):
        return True
    return False


def is_macports_env():
    """
    Check if Python interpreter was installed via Macports command 'port'.

    :return: True if Macports else otherwise.
    """
    # Python path prefix should start with Macports prefix.
    env_prefix = get_macports_prefix()
    if env_prefix and base_prefix.startswith(env_prefix):
        return True
    return False


def get_homebrew_prefix():
    """
    :return: Root path of the Homebrew environment.
    """
    prefix = shutil.which('brew')
    # Conversion:  /usr/local/bin/brew -> /usr/local
    prefix = os.path.dirname(os.path.dirname(prefix))
    return prefix


def get_macports_prefix():
    """
    :return: Root path of the Macports environment.
    """
    prefix = shutil.which('port')
    # Conversion:  /usr/local/bin/port -> /usr/local
    prefix = os.path.dirname(os.path.dirname(prefix))
    return prefix


def fix_exe_for_code_signing(filename):
    """
    Fixes the Mach-O headers to make code signing possible.

    Code signing on OS X does not work out of the box with embedding
    .pkg archive into the executable.

    The fix is done this way:
    - Make the embedded .pkg archive part of the Mach-O 'String Table'.
      'String Table' is at end of the OS X exe file so just change the size
      of the table to cover the end of the file.
    - Fix the size of the __LINKEDIT segment.

    Mach-O format specification:

    http://developer.apple.com/documentation/Darwin/Reference/ManPages/man5/Mach-O.5.html
    """
    exe_data = MachO(filename)
    # Every load command is a tupple: (cmd_metadata, segment, [section1, section2])
    cmds = exe_data.headers[0].commands  # '0' - Exe contains only one architecture.
    file_size = exe_data.headers[0].size

    ## Make the embedded .pkg archive part of the Mach-O 'String Table'.
    # Data about 'String Table' is in LC_SYMTAB load command.
    for c in cmds:
        if c[0].get_cmd_name() == 'LC_SYMTAB':
            data = c[1]
            # Increase the size of 'String Table' to cover the embedded .pkg file.
            new_strsize = file_size - data.stroff
            data.strsize = new_strsize
    ## Fix the size of the __LINKEDIT segment.
    # __LINKEDIT segment data is the 4th item in the executable.
    linkedit = cmds[3][1]
    new_segsize = file_size - linkedit.fileoff
    linkedit.filesize = new_segsize
    linkedit.vmsize = new_segsize
    ## Write changes back.
    with open(exe_data.filename, 'rb+') as fp:
        exe_data.write(fp)


def get_osx_dylib_framework_path(libpath):
    """
    Checks if the given dynamic library belongs to a framework bundle,
    by checking the parent components of the path.

    :return: path component corresponding to the framework bundle's
    top-level directory if the library belongs to one, None otherwise.
    """
    libpath = pathlib.PurePath(libpath)
    framework_name = str(libpath.name) + ".framework"  # Derive framework name
    # Check all parents
    for parent in libpath.parents:
        if parent.name == framework_name:
            return str(parent)
    return None


_registered_fwk_relocations = {}

def osx_register_framework_relocation(fwk_name, path):
    """
    Register a framework bundle relocation for given framework name and
    a _MEIPASS dir relative path. During the lookup, fnmatch() function
    is used, so the name may contain * and/or ? to cover a range of
    framework names. If multiple relocations with overlapping names
    are defined, the order of resolution is undefined.
    """
    _registered_fwk_relocations[fwk_name] = path


def get_osx_framework_relocation_path(fwk_name):
    """
    Retrieve optional relocation path for the given framework name.

    :return: relative path to _MEIPASS dir where the framework bundle
    directory should be relocated if available, empty string otherwise.
    """
    for reloc_name, reloc_path in _registered_fwk_relocations.items():
        if fnmatch.fnmatch(fwk_name, reloc_name):
            return reloc_path
    return ''
