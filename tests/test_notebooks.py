"""
Notebooks tests
----------------

Execute all notebooks.

"""

import os

from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.exporters import Exporter, HTMLExporter


def notebook_tester(fname):
    raw_nb = Exporter().from_filename(fname)
    raw_nb[0].metadata.setdefault('kernelspec', {})['name'] = 'python'
    preproc = ExecutePreprocessor(timeout=-1)
    exec_nb = preproc.preprocess(*raw_nb)

    out_nb = HTMLExporter().from_notebook_node(*exec_nb)
    fout = fname.replace('.ipynb', '.html')
    with open(fout, 'w') as f:
        f.write(out_nb[0])


if __name__ == '__main__':
    import glob

    rootpath = os.path.join(os.path.abspath(os.path.pardir), 'notebooks')
    nblist = glob.glob(os.path.join(rootpath, '**', '*.ipynb'))

    for ipynb in sorted(nblist):
        print('Running notebook: {}'.format(ipynb))
        notebook_tester(ipynb)
