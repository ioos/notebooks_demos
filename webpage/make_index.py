import os
import glob
from nbconvert.exporters import markdown

SITE_DIR = '.'
IMAGE_DIR = os.path.join(SITE_DIR, 'images')


def extract_thumbnail_and_title(nb_path):
    title = 'No title'
    image = 'images/placeholder.png'
    exporter = markdown.MarkdownExporter()
    output, resources = exporter.from_filename(nb_path)
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('#'):
            title = line.strip('#').strip()
            break

    images = sorted(resources['outputs'])
    if images:
        img_file = images[-1]
        thumb_name = os.path.join(
            IMAGE_DIR,
            os.path.splitext(os.path.basename(nb_path))[0] +
            os.path.splitext(img_file)[-1]
            )

        with open(os.path.join('code_gallery', thumb_name), 'wb') as thumb:
            thumb.write(resources['outputs'][img_file])
            print(thumb_name)

        image = os.path.relpath(thumb_name, SITE_DIR)
    return title, image


if __name__ == '__main__':
    base_url = '{{ site.url }}{{ site.baseurl }}/'
    box = '<div><a href="{base_url}/notebooks/{fname}"><figcaption>{caption}</figcaption><img src="{img}"></a></div>\n'.format  # noqa
    front_matter = """\
---
title: Code Gallery
layout: single
---

"""

    with open(os.path.join(SITE_DIR, 'code_gallery.md'), 'w') as index:
        index.write(front_matter)
        index.write('<div id="gallery">\n')

        notebooks = glob.glob(os.path.join(os.path.pardir, 'notebooks', '*.ipynb'))
        for fname in sorted(notebooks, reverse=True):
            caption, img = extract_thumbnail_and_title(fname)
            fname, ext = os.path.splitext(os.path.basename(fname))
            index.write(
                box(caption=caption, base_url=base_url, fname=fname, img=img)
            )

        index.write('</div>\n')
