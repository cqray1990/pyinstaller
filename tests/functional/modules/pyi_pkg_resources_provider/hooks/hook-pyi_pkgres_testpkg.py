from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('pyi_pkgres_testpkg', excludes=['**/__pycache__', ])
