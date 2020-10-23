#-----------------------------------------------------------------------------
# Copyright (c) 2013-2020, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------


import pkg_resources as res
from pyimod03_importers import FrozenImporter


# To make pkg_resources work with frozen modules we need to set the 'Provider'
# class for FrozenImporter. This class decides where to look for resources
# and other stuff. 'pkg_resources.NullProvider' is dedicated to PEP302
# import hooks like FrozenImporter is. It uses method __loader__.get_data() in
# methods pkg_resources.resource_string() and pkg_resources.resource_stream()

# We subclass the NullProvider and implement _has(), _isdir(), and _listdir(),
# which are needed for pkg_resources.has_resource(), pkg_resources.resource_isdir(),
# and pkg_resources.resource_listdir() to work. We cannot use the DefaultProvider,
# because it provides filesystem-only implementations (and overrides _get()
# with a filesystem-only one), whereas our provider needs to also support
# embedded resources.

class PyiFrozenProvider(res.NullProvider):
    def __init__(self, module):
        super().__init__(module)

    def _has(self, path):
        return os.path.exists(path)

    def _isdir(self, path):
        return os.path.isdir(path)

    def _listdir(self, path):
        return os.listdir(path)

res.register_loader_type(FrozenImporter, PyiFrozenProvider)
