import os
import sys
try:
    from urllib2 import quote
except ImportError:
    from urllib.parse import quote

BLOG_DIR = os.path.abspath(os.path.curdir)

fname = None
for arg in sys.argv:
    if arg.endswith('.ipynb'):
        fname = arg.split('.ipynb')[0]
        break

c = get_config()
c.NbConvertApp.export_format = 'markdown'
c.MarkdownExporter.template_path = ['.']
c.MarkdownExporter.template_file = 'jekyll'


def path2support(path):
    """Turn a file path into a URL."""
    parts = path.split(os.path.sep)
    #res = '{{ site.baseurl}}notebooks/' + '/'.join(quote(part) for part in parts)
    res = '{{ site.baseurl}}/' + '/'.join(quote(part) for part in parts)
    return res

c.MarkdownExporter.filters = {'path2support': path2support}

if fname:
    c.NbConvertApp.output_base = fname.lower().replace(' ', '-')
    c.FilesWriter.build_directory = BLOG_DIR
    #c.FilesWriter.build_directory = BLOG_DIR + '/notebooks'
