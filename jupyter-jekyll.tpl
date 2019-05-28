{% extends 'display_priority.tpl' %}

{%- block header -%}
---
title: "{{resources['metadata']['title']}}"
layout: notebook
{# permalink: {{resources['metadata']['permalink']}} #}
---
{%- endblock header -%}

{% block in_prompt %}
<div class="prompt input_prompt">
In&nbsp;[{{ cell.execution_count }}]:
</div>
{% endblock in_prompt %}

{% block output_prompt %}
{%- endblock output_prompt %}

{% block input %}
```{% if nb.metadata.language_info %}{{ nb.metadata.language_info.name }}{% endif %}
{{ cell.source }}
```
{% endblock input %}

{% block error %}
{{ super() }}
{% endblock error %}

{% block traceback_line %}
{{ line | indent | strip_ansi }}
{% endblock traceback_line %}

{% block execute_result %}

{% block data_priority scoped %}
{{ super() }}
{% endblock %}
{% endblock execute_result %}

{% block stream %}
{%- if output.name == 'stderr' -%}
<div class="warning" style="border:thin solid red">
{{ output.text | indent(4) | wrap_text(80) }}
</div>
{%- else -%}
<div class="output_area"><div class="prompt"></div>
<pre>
{{ output.text | indent(4) }}
</pre>
</div>
{%- endif -%}
{% endblock stream %}

{% block data_svg %}
{{ output.data['image/svg+xml'] }}
{% endblock data_svg %}

{% block data_png %}
![png](data:image/png;base64,{{ output.data['image/png'] }})
{% endblock data_png %}

{% block data_latex %}
{{ output.data['text/latex'] }}
{% endblock data_latex %}

{% block data_html scoped %}
{{ output.data['text/html'] }}
{% endblock data_html %}

{% block data_markdown scoped %}
{{ output.data['text/markdown'] }}
{% endblock data_markdown %}

{% block data_text scoped %}
{{ output.data['text/plain'] | indent }}
{% endblock data_text %}

{% block markdowncell scoped %}
{{ cell.source }}
{% endblock markdowncell %}

{% block unknowncell scoped %}
unknown type  {{ cell.type }}
{% endblock unknowncell %}


{%- block footer -%}
<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/{{resources['metadata']['name']}}.ipynb)
this notebook, or click [here](https://binder.pangeo.io/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/{{resources['metadata']['name']}}.ipynb) to run a live instance of this notebook.
{%- endblock footer -%}
