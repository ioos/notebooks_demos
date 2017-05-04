"""
Notebooks tests
----------------

Check notebook coding standards.

(Works only for Python Jupyter notebooks.)

"""

import os
import sys

from glob import glob

from utilities import check_coding_standard


_root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

nblist = glob(os.path.join(_root_path, 'notebooks', '*.ipynb'))

passed = True
for ipynb in sorted(nblist):
    try:
        check_coding_standard(ipynb)
        print('[PASSED]: {}'.format(os.path.split(ipynb)[-1]))
    except Exception as e:
        print('[FAILED]: {}'.format(os.path.split(ipynb)[-1]))
        print(e)
        passed = False

sys.exit(1) if not passed else sys.exit(0)
