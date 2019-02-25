import os
from urllib.parse import quote


def path2url(path):
    """Turn a file path into a URL"""
    parts = path.split(os.path.sep)
    return "{{ site.baseurl }}/notebooks/" + "/".join(
        quote(part) for part in parts
    )


c = get_config()  # noqa
c.NbConvertApp.export_format = "markdown"
c.MarkdownExporter.template_file = "jupyter-jekyll"
c.FilesWriter.build_directory = "webpage/_notebooks"
c.MarkdownExporter.filters = {"path2url": path2url}
c.Exporter.preprocessors = ["nbconvert_utils.JekyllPreprocessor"]
# We do not need to rename for the current date. We actually want to freeze the date.
# c.NbConvertApp.postprocessor_class = 'nbconvert_utils.Rename'
