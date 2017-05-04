"""
Notebooks tests
----------------

Common utilities functions.

"""

import os

from flake8.api import legacy as flake8
from nbconvert import PythonExporter
from nbconvert.exporters import Exporter
from nbconvert.preprocessors import ExecutePreprocessor
from tempfile import mkstemp


kernels = {
    'R': 'ir',
    'octave': 'octave',
    'matlab': 'octave',
    'python': 'python',
    'python2': 'python',
    'python3': 'python',
}

_root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def load_notebook(fname):
    notebook, resources = Exporter().from_filename(fname)
    return notebook, resources


def get_language(notebook):
    return notebook['metadata']['kernelspec']['language']


def convert_to_python(notebook, template_file=None):
    exporter = PythonExporter()
    exporter.template_file = template_file
    notebook_code, meta = exporter.from_notebook_node(notebook)
    return notebook_code, meta


def check_style(notebook_code):
    """
    The notebook PEP 8 test ignore:
    W292: blank line at end of file (always present when using nbconvert)
    E226: missing whitespace around arithmetic operator (not enforced by PEP 8)
    E402: module level import not at top of file (for notebooks it is clearer
    to import at the top of the cell of its first use.)

    """
    lines = notebook_code.split('\n')
    notebook_code = '\n'.join(
        [line for line in lines if not line.startswith('get_ipython')]
        )
    fid, fname = mkstemp(suffix='.py', prefix='temp_script_')
    with open(fname, 'w') as f:
        f.write(notebook_code.strip())
    style_guide = flake8.get_style_guide(
        ignore=['W292', 'E226', 'E402'],
        max_line_length=100
        )
    report = style_guide.input_file(fname)
    os.close(fid)
    return report


def check_coding_standard(fname):
    notebook, _ = load_notebook(fname)
    language = get_language(notebook)

    # We lint only the python notebooks.
    if language.startswith('python'):
        template_file = os.path.join(_root_path, 'tests', 'strip_markdown.tpl')
        notebook_code, _ = convert_to_python(notebook, template_file)
        report = check_style(notebook_code)
        error = '\n'.join(report.get_statistics('E'))
        assert report.get_statistics('E') == [], '{}\n{}'.format(fname, error)


def notebook_tester(fname, kernelspec='python'):
    raw_nb = Exporter().from_filename(fname)
    raw_nb[0].metadata.setdefault('kernelspec', {})['name'] = kernelspec
    preproc = ExecutePreprocessor(timeout=-1)
    preproc.preprocess(*raw_nb)


def test_run(fname):
    notebook, _ = load_notebook(fname)
    language = get_language(notebook)
    kernelspec = kernels[language]
    # FIXME: we cannot run MatlabTM/Octave on Travis yet.
    if kernelspec == 'octave':
        print('Cannot run {} with kernel {}'.format(fname, language))
    else:
        notebook_tester(fname, kernelspec=kernelspec)
