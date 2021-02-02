import datetime
import os
import re

from nbconvert.postprocessors import PostProcessorBase
from nbconvert.preprocessors import Preprocessor


class JekyllPreprocessor(Preprocessor):
    def preprocess(self, nb, resources):
        # skipped cells that are marked with the skip metadata
        cells = []
        for cell in nb.cells:
            if cell.metadata.get("skip", False):
                continue
            cells.append(cell)
        nb.cells = cells

        # extract the title
        first = nb.cells[0]
        if first.cell_type == "markdown":
            lines = first.source.split("\n")
            m = re.match(r"^#(?P<title>[^#]+)", lines[0])
            if m:
                resources["metadata"]["title"] = m.groupdict()["title"].strip()
                self.log.info('Title is "{}"'.format(resources["metadata"]["title"]))
                if len(lines) == 1:
                    nb.cells = nb.cells[1:]
                else:
                    first.source = "\n".join(lines[1:])

        # extract other metadata
        now = datetime.datetime.now()
        name = resources["unique_key"]
        resources["metadata"]["date"] = now.strftime("%Y-%m-%d %H:%M:%S")
        resources["metadata"]["permalink"] = "{}/{}".format(
            now.strftime("/%Y/%m/%d"),
            name,
        )
        resources["metadata"]["categories"] = nb.metadata.get("categories", None)
        resources["metadata"]["tags"] = nb.metadata.get("tags", None)

        return super(JekyllPreprocessor, self).preprocess(nb, resources)

    def preprocess_cell(self, cell, resources, cell_index):
        return cell, resources


class Rename(PostProcessorBase):
    def postprocess(self, path):
        now = datetime.datetime.now()
        dirname, filename = os.path.split(path)
        name = os.path.splitext(filename)[0]
        new_name = "{year}-{month:02d}-{day:02d}-{name}.md".format(
            year=now.year,
            month=now.month,
            day=now.day,
            name=name,
        )
        new_path = os.path.join("source", "_posts", new_name)
        self.log.info("Renaming '{}' --> '{}'".format(path, new_path))
        os.rename(path, new_path)
