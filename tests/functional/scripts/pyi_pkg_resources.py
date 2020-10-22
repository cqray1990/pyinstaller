modname = 'pyi_pkgres_testmod'

from pkg_resources import resource_exists, resource_isdir, resource_listdir

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


########################################################################
#                Validate behavior of resource_exists()                #
########################################################################
# Module's top-level directory: returns true for default provider,
# false for zipped egg. So allow either...
assert resource_exists(modname, '.') in [True, False]

# Submodule's directory: accessing it from top-level module returns
# True for both default and zipped egg provider. Accessing it from the
# submodule itself, however, returns True and False for default and egg,
# respectively.
assert resource_exists(modname, 'submod') == True
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


########################################################################
#                Validate behavior of resource_isdir()                 #
########################################################################
# Module's top-level directory: returns true for default provider,
# false for zipped egg. So allow either...
assert resource_isdir(modname, '.') in [True, False]

# Submodule's directory: accessing it from top-level module returns
# True for both default and zipped egg provider. Accessing it from the
# submodule itself, however, returns True and False for default and egg,
# respectively.
assert resource_isdir(modname, 'submod') == True
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


########################################################################
#               Validate behavior of resource_listdir()                #
########################################################################
# List module's top-level directory: default provider lists content,
# while zipped egg returns empty list. So allow either...
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


# Attempt to list an non-existant directory in main module. With default
# provider, this raises FileNotFoundError, while zipped egg returns
# empty list
try:
    content = resource_listdir(modname, 'non-existant')
except FileNotFoundError:
    pass  # good
except:
    raise
else:
    assert content == [], "Expected FileNotFoundError or empty list!"

# Attempt to list an non-existant directory in submodule. With default
# provider, this raises FileNotFoundError, while zipped egg returns
# empty list
try:
    content = resource_listdir(modname + '.submod', 'data/non-existant')
except FileNotFoundError:
    pass  # good
except:
    raise
else:
    assert content == [], "Expected FileNotFoundError or empty list!"
