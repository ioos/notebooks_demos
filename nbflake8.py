import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import easyargs
import nbconvert


@contextmanager
def _tmpnotebook(data, fname="notebook"):
    filepath = ""
    try:
        fid, filepath = tempfile.mkstemp(suffix=".py", prefix=f"{fname}_")
        os.write(fid, data.encode("utf8"))
        os.write(fid, b"\n")
        os.close(fid)
        yield filepath
    finally:
        if os.path.isfile(filepath):
            print(filepath)
            os.remove(filepath)


def _notebook_to_py(notebook):
    exporter = nbconvert.PythonExporter()
    exporter.exclude_markdown = True
    exporter.exclude_output = True
    exporter.exclude_raw = True
    exporter.exclude_unknown = True
    exporter.exclude_header = True
    body, resources = exporter.from_file(notebook)
    # Remove magic commands.
    body = body.replace("get_ipython()", "# get_ipython()")
    # The last two elements are a lint added by nbconvert (extra lines).
    return body[:-2]


@easyargs
def lint(notebook):
    ignore = [
        "E226",  # Missing whitespace around arithmetic operator.
        "E402",  # Module level import not at top of file.
        "E703",  # Statement ends with a semicolon.
        "E731",  # Do not assign a lambda expression, use a def.
        "I100",  # Your import statements are in the wrong order.
        "I201",  # Missing newline between import groups.
        "I202",  # Additional newline in a group of imports.
        "W391",  # Blank line at end of file.
        "W504",  # Line break after binary operator.
    ]
    code = _notebook_to_py(notebook)
    p = Path(notebook)
    with _tmpnotebook(code, fname=p.stem) as tmp:
        proc = subprocess.Popen(
            [
                "flake8",
                tmp,
                f'--ignore={",".join(ignore)}',
                "--show-source",
                "--max-line-length=999",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out = proc.communicate()[0]
        sys.stdout.write("".join(out.decode()))
        sys.stdout.flush()
        sys.exit(proc.returncode)


if __name__ == "__main__":
    lint()
