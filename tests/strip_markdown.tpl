{% extends 'python.tpl'%}
{% block markdowncell -%}
{% endblock markdowncell %}

{% block in_prompt %}
# This was input cell with execution count: {{ cell.execution_count if cell.execution_count else ' ' }}
{%- endblock in_prompt %}
