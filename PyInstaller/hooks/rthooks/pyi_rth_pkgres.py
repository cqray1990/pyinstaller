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
    def __init__(self, toc_files, toc_dirs=[]):
        # Reconstruct the fileystem hierarchy by building a trie from
        # the given file and directory paths
        self._tree = dict()

        # Data files
        for path in toc_files:
            path = pathlib.PurePath(path)
            current = self._tree

            for component in path.parts[:-1]:
                current = current.setdefault(component, {})
            current[path.parts[-1]] = ''

        # Extra directories
        for path in toc_dirs:
            path = pathlib.PurePath(path)
            current = self._tree

            for component in path.parts:
                current = current.setdefault(component, {})


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

        return list(node.keys())


class PyiFrozenProvider(res.NullProvider):
    def __init__(self, module):
        super().__init__(module)

        # Construct relative package/module path for searching the TOC
        # NOTE: construct the path from module.__file__ instead of using
        # module.__path__, because the latter is available only for
        # packages and not for their modules
        pkg_path = os.path.dirname(module.__file__)
        pkg_path = pkg_path[SYS_PREFIXLEN+1:]

        # Reconstruct package name prefix (use package path to obtain
        # correct prefix in case of module)
        pkg_name = '.'.join(pathlib.PurePath(pkg_path).parts)

        # Collect relevant entries from TOC. We are interested in either
        # files that are located in the package/module's directory (data
        # files) or in packages that are prefixed with package/module's
        # name (to reconstruct subpackage directories)
        data_files = []
        package_dirs = []

        for entry in self.loader.toc:
            if entry.startswith(pkg_path + os.path.sep):
                # Data file path
                data_files.append(entry)
            elif entry.startswith(pkg_name) and self.loader.is_package(entry):
                # Package or subpackage; convert the name to directory path
                package_dir = os.path.sep.join(entry.split('.'))
                package_dirs.append(package_dir)

        # Reconstruct the filesystem
        self.embedded_tree = _TocFilesystem(data_files, package_dirs)

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
