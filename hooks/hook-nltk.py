#-----------------------------------------------------------------------------
# Copyright (c) 2005-2018, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


# hook for nltk
import nltk
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect NLTK data files
datas = collect_data_files('nltk', include_py_files=True)

# loop through the data directories and add them
# for p in nltk.data.path:
#     datas.append((p, "nltk_data"))

datas.append(("C:\\Users\\Houssem\\AppData\\Roaming\\nltk_data", "nltk_data"))

# nltk.chunk.named_entity should be included
hiddenimports = collect_submodules('nltk')
