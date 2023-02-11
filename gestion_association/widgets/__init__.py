import sys
from html import escape
from string import capwords

from django.forms import SelectMultiple, CheckboxInput
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from rest_framework.utils import json

class TableSelectMultiple(SelectMultiple):
    """
    Provides selection of items via checkboxes, with a table row
    being rendered for each item, the first cell in which contains the
    checkbox.
    Only for use with a ModelMultipleChoiceField
    """
    def __init__(
        self,
        item_attrs,
        enable_shift_select=False,
        enable_datatables=False,
        bootstrap_style=False,
        datatable_options={},
        *args,
        **kwargs
    ):
        """
        item_attrs
            Defines the attributes of each item which will be displayed
            as a column in each table row, in the order given.
            Any callables in item_attrs will be called with the item to be
            displayed as the sole parameter.
            Any callable attribute names specified will be called and have
            their return value used for display.
            All attribute values will be escaped.
        """
        super(TableSelectMultiple, self).__init__(*args, **kwargs)
        self.item_attrs = item_attrs
        self.enable_shift_select = enable_shift_select
        self.enable_datatables = enable_datatables
        self.bootstrap_style = bootstrap_style
        self.datatable_options = datatable_options

    def _datatable_javascript(self, name):
        # Note: Paging cannot be easily turned on, because otherwise
        # the checkboxes on unvisible pages are not in the request.
        datatable_options = {
            "order": [],
            "paging": False,
            "searching": False,
            "columnDefs": [
                {
                    "targets": 'no-sort',
                    "orderable": False,
                },
            ],
        }
        datatable_options |= self.datatable_options
        js = "$(document).ready(function(){{$('#{}').DataTable({}); }});"
        return js.format(escape(name), json.dumps(datatable_options))

    def render(self, name, value,
               attrs=None, choices=(), renderer=None, **kwargs):
        if value is None:
            value = []
        table_classes = "display"
        if self.bootstrap_style:
            table_classes += " table table-sm table-bordered"
        output = [f'<table id={escape(name)} class="{table_classes}">']
        head = self.render_head()
        output.append(head)
        body = self.render_body(name, value, attrs, **kwargs)
        output.extend((body, '</table>', '<script>'))
        if self.enable_datatables:
            output.append(self._datatable_javascript(name))

        output.append('</script>')
        return mark_safe('\n'.join(output))

    def render_head(self):
        output = ['<thead><tr><th class="no-sort"></th>']
        for item in self.item_attrs:
            name = item if isinstance(item, str) else item[1]
            output.append(f'<th>{clean_underscores(escape(name))}</th>')
        output.append('</tr></thead>')
        return ''.join(output)

    def render_body(self, name, value, attrs, **kwargs):
        output = ['<tbody>']
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs)
        final_attrs['class'] = "tableselectmultiple selectable-checkbox"
        if self.bootstrap_style:
            final_attrs['class'] += " form-check-input"
        str_values = {force_str(v) for v in value}
        choice_pks = [pk.value for (pk, item) in self.choices]
        choices = self.choices.queryset.filter(pk__in=choice_pks)
        for i, item in enumerate(choices):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id=f"{attrs['id']}_{i}")
            cb = CheckboxInput(final_attrs,
                               check_test=lambda value: value in str_values)
            option_value = force_str(item.pk)
            rendered_cb = cb.render(name, option_value, **kwargs)
            output.append(f'<tr><td>{rendered_cb}</td>')
            for item_attr in self.item_attrs:
                attr = item_attr \
                        if isinstance(item_attr, str) \
                        else item_attr[0]
                content = get_underscore_attrs(attr, item)
                output.append(f'<td>{escape(str(content))}</td>')
            output.append('</tr>')
        output.append('</tbody>')
        return ''.join(output)


def get_underscore_attrs(attrs, item):
    for attr in attrs.split('__'):
        if callable(attr):
            item = attr(item)
        elif callable(getattr(item, attr)):
            item = getattr(item, attr)()
        else:
            item = getattr(item, attr)
    return "" if item is None else item


def clean_underscores(string):
    """
    Helper function to clean up table headers.  Replaces underscores
    with spaces and capitalizes words.
    """
    return capwords(string.replace("_", " "))