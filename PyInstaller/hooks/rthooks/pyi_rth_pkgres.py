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

import os
import sys
import pathlib

import pkg_resources as res
from pyimod03_importers import FrozenImporter

SYS_PREFIX = sys._MEIPASS
SYS_PREFIXLEN = len(SYS_PREFIX)

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

class _TocFilesystem:
    def __init__(self, toc):
        self._tree = self._build_tree(toc)

    def _build_tree(self, toc):
        root = dict()
        for path in toc:
            path = pathlib.PurePath(path)
            current = root

            for component in path.parts[:-1]:
                current = current.setdefault(component, {})
            current[path.parts[-1]] = ''

        return root

    def _get_tree_node(self, path):
        path = pathlib.PurePath(path)

        current = self._tree
        for component in path.parts:
            if component not in current:
                return None
            current = current[component]

        return current


    def path_exists(self, path):
        node = self._get_tree_node(path)
        return node is not None  # File or directory


    def path_isdir(self, path):
        node = self._get_tree_node(path)

        if node is None:
            return False  # Non-existant

        if isinstance(node, str):
            return False  # File

        return True

    def path_listdir(self, path):
        node = self._get_tree_node(path)

        if not isinstance(node, dict):
            return []  # Non-existant or file

        return node.keys()


class PyiFrozenProvider(res.NullProvider):
    def __init__(self, module):
        super().__init__(module)

        # Construct relative module path for searching the TOC
        module_path = module.__path__[0][SYS_PREFIXLEN+1:]

        # Collect entries from TOC that are located within the module
        # and are not Python modules/packages. These correspond to
        # embedded data entries
        data_paths = [x for x in self.loader.toc if
            x.startswith(module_path) and
            not self.loader.is_package(x)
        ]

        # Reconstruct the filesystem
        self.embedded_tree = _TocFilesystem(data_paths)

    def _has(self, path):
        assert path.startswith(SYS_PREFIX + os.path.sep)
        rel_path = path[SYS_PREFIXLEN+1:]

        return self.embedded_tree.path_exists(rel_path) or os.path.exists(path)

    def _isdir(self, path):
        assert path.startswith(SYS_PREFIX + os.path.sep)
        rel_path = path[SYS_PREFIXLEN+1:]

        return self.embedded_tree.path_isdir(rel_path) or os.path.isdir(path)

    def _listdir(self, path):
        assert path.startswith(SYS_PREFIX + os.path.sep)
        rel_path = path[SYS_PREFIXLEN+1:]

        # List content from embedded filesystem...
        content = self.embedded_tree.path_listdir(rel_path)

        # ... as well as the actual one
        if os.path.isdir(path):
            content += os.listdir(path)

        return content

res.register_loader_type(FrozenImporter, PyiFrozenProvider)
