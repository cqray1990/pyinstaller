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

# TODO: remove this hook during PyInstaller 4.5 release cycle!

from PyInstaller.utils.hooks import exec_statement, collect_submodules

# We need to collect submodules from win32ctypes.core.cffi or
# win32ctypes.core.ctypes for win32ctypes.core to work. The use of
# the backend is determined by availability of cffi.
cffi_available = exec_statement(
    """try:import cffi;print('\\nTrue')\nexcept: print('\\nFalse')"""
).split()[-1] == 'True'

if cffi_available:
    hiddenimports = collect_submodules('win32ctypes.core.cffi')
else:
    hiddenimports = collect_submodules('win32ctypes.core.ctypes')
