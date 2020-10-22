from pkg_resources import resource_exists, resource_isdir, resource_listdir
modname = 'pyi_pkgres_testmod'

########################################################################
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

########################################################################
#                Validate behavior of resource_exists()                #
########################################################################
# Module's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
assert resource_exists(modname, '.') in [True, False]

# Submodule's directory (relative to module):
#  * both DefaultProvider and ZipProvider return True
assert resource_exists(modname, 'submod') == True

# Submodule directory (relative to submodule):
#  * DefaultProvider returns True
#  * ZipProvider returns False
assert resource_exists(modname + '.submod', '.') in [True, False]

# Data directory in submodule
assert resource_exists(modname, 'submod/data') == True
assert resource_exists(modname + '.submod', 'data') == True

# Subdirectory in data directory
assert resource_exists(modname, 'submod/data/extra') == True
assert resource_exists(modname + '.submod', 'data/extra') == True
#assert resource_exists(modname + '.submod.data', 'extra') == True

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
assert resource_exists(modname, '..') in [True, False]

# Parent of submodule
#  * DefaultProvider returns True
#  * ZipProvider returns False
assert resource_exists(modname + '.submod', '..') in [True, False]


########################################################################
#                Validate behavior of resource_isdir()                 #
########################################################################
# Module's directory
#  * DefaultProvider returns True
#  * ZipProvider returns False
assert resource_isdir(modname, '.') in [True, False]

# Submodule's directory (relative to module):
#  * both DefaultProvider and ZipProvider return True
assert resource_isdir(modname, 'submod') == True

# Submodule directory (relative to submodule):
#  * DefaultProvider returns True
#  * ZipProvider returns False
assert resource_isdir(modname + '.submod', '.') in [True, False]

# Data directory in submodule
assert resource_isdir(modname, 'submod/data') == True
assert resource_isdir(modname + '.submod', 'data') == True

# Subdirectory in data directory
assert resource_isdir(modname, 'submod/data/extra') == True
assert resource_isdir(modname + '.submod', 'data/extra') == True
#assert resource_isdir(modname + '.submod.data', 'extra') == True

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
assert resource_isdir(modname, '..') in [True, False]

# Parent of submodule
#  * DefaultProvider returns True
#  * ZipProvider returns False
assert resource_isdir(modname + '.submod', '..') in [True, False]


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
assert content == expected or content == set()

# List submodule directory
expected = {'__init__.py', 'data'}
content = resource_listdir(modname, 'submod')
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
content = set(content)
assert content == expected

# List data directory in submodule
expected = {'entry1.txt', 'entry2.txt', 'entry3.txt', 'extra'}

content = resource_listdir(modname, 'submod/data')
content = set(content)
assert content == expected

content = resource_listdir(modname + '.submod', 'data')
content = set(content)
assert content == expected

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
    pass  # good
except:
    raise
else:
    assert content == [], "Expected NotADirectoryError or empty list!"


# Attempt to list an non-existant directory in main module.
#  * DefaultProvider raises FileNotFoundError
#  * ZipProvider returns empty list
try:
    content = resource_listdir(modname, 'non-existant')
except FileNotFoundError:
    pass  # good
except:
    raise
else:
    assert content == [], "Expected FileNotFoundError or empty list!"

# Attempt to list an non-existant directory in submodule
#  * DefaultProvider raises FileNotFoundError
#  * ZipProvider returns empty list
try:
    content = resource_listdir(modname + '.submod', 'data/non-existant')
except FileNotFoundError:
    pass  # good
except:
    raise
else:
    assert content == [], "Expected FileNotFoundError or empty list!"


# Attempt to list module's parent
#  * DefaultProvider actually lists the parent directory
#  * ZipProvider returns empty list
content = resource_listdir(modname, '..')
content = set(content)
assert modname in content or content == set()

# Attempt to list submodule's parent
#  * DefaultProvider actually lists the parent directory
#  * ZipProvider returns empty list
expected = {'__init__.py', 'submod'}
content = resource_listdir(modname + '.submod', '..')
content = set(content)
if '__pycache__' in content:
    content.remove('__pycache__')  # ignore __pycache__
assert content == expected or content == set()
