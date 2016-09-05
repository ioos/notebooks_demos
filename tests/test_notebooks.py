"""
Notebooks tests
----------------

Execute all notebooks.

"""

from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.exporters import Exporter, HTMLExporter


def notebook_tester(fname):
    raw_nb = Exporter().from_filename(fname)
    raw_nb[0].metadata.setdefault('kernelspec', {})['name'] = 'python'
    preproc = ExecutePreprocessor(timeout=-1)
    try:
        exec_nb = preproc.preprocess(*raw_nb)
    except Exception as e:
        return '[Failed]\n{}'.format(e)

    out_nb = HTMLExporter().from_notebook_node(*exec_nb)
    fout = fname.replace('.ipynb', '.html')
    with open(fout, 'w') as f:
        f.write(out_nb[0])
    return '[Passed]'


if __name__ == '__main__':
    import os
    import glob

    rootpath = os.path.join(os.path.abspath(os.path.pardir), 'notebooks')
    nblist = glob.glob(os.path.join(rootpath, '**', '*.ipynb'))

    for ipynb in sorted(nblist):
        print('[Running notebook]: {}'.format(ipynb))
        ret = notebook_tester(ipynb)
        print('{}\n'.format(ret))
