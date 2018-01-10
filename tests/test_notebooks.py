"""
Notebooks tests
----------------

Execute published notebooks.

"""

import os
import sys

from glob import glob

from utilities import test_run

_root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

nblist = glob(os.path.join(_root_path, 'notebooks', '*.ipynb'))


passed = True
for ipynb in sorted(nblist):
    skip = ['2017-11-30-rerddap.ipynb']
    fname = os.path.split(ipynb)[-1]
    if fname in skip:
        continue
    try:
        test_run(ipynb)
        print('[PASSED]: {}'.format(fname))
    except Exception as e:
        print('[FAILED]: {}'.format(fname))
        print(e)
        passed = False

sys.exit(1) if not passed else sys.exit(0)
