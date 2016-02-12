"""Assortment of helpers to print/manipulate data."""
import tempfile
import os
import csv
import shutil
from .config import get_config_section
from tabulate import tabulate

_html_options = get_config_section("HTMLOptions")
_console_options = get_config_section("ConsoleOptions")


def to_html(data):
    if not data:
        return
    fields = data[0]._fields

    row_template = ('<tr>' + ''.join("<td>{" + f + "}</td>"
                    for f in fields) + '</tr>')
    header_footer_text = ''.join("<th>" + f + "</th>" for f in fields)

    mark_up = ["""<TABLE id="tbResultSet" class="cell-border" cellspacing="0" width="100%">"""]
    mark_up.append('<thead><TR>')
    mark_up.append(header_footer_text)
    mark_up.append('</TR></thead>')
    mark_up.append('<tfoot><TR>')
    mark_up.append(header_footer_text)
    mark_up.append('</TR></tfoot>')
    mark_up.append('<tbody>')
    for row in data:
        mark_up.append(row_template.format_map(row._asdict()))
    mark_up.append('</tbody>')
    mark_up.append("</TABLE>")

    htmlfile_handle, htmlpath = tempfile.mkstemp(".htm", text=True)
    tmp = _html_options["Template_HTML"]
    tmp = tmp.replace("{{TABLE MARK UP}}", "\n".join(mark_up))
    tmp = tmp.replace("{{SCRIPT DIR}}",
                      os.path.dirname(os.path.realpath(__file__)) +
                      "\\resources")
    print("Creating and opening temp file", htmlpath)
    with os.fdopen(htmlfile_handle, mode="w", encoding="UTF-8") as f:
        f.write(tmp)
    os.startfile(htmlpath)


def to_csv(data):
    if not data:
        return
    fields = data[0]._fields
    csvfile_handle, csvpath = tempfile.mkstemp(".csv", text=True)
    print("Creating and opening temp file", csvpath)
    with os.fdopen(csvfile_handle, mode="w", encoding="UTF-8",
                   newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row._asdict())
    os.startfile(csvpath)


def to_console(data):
    if not data:
        return

    fields = [_console_column_formatter(f) for f in data[0]._fields]
    # a copy of the data, pre-formatted
    data_as_dicts = [r._asdict() for r in data]
    formatted_data = []
    for d in data_as_dicts:
        row = tuple(map(_console_column_formatter, d.values()))
        formatted_data.append(row)
    col_count = _console_cols_to_fit(fields, formatted_data)
    console_text = tabulate((x[:col_count] for x in formatted_data),
                            headers=fields)
    print(console_text)
    if col_count < len(fields):
        print("\n", col_count, "out of", len(fields), " columns visible.")

def _console_column_formatter(value):
    value = str(value)
    max_length = int(_console_options['Max_Col_Length'])
    if len(value) > max_length:
        value = value[:max_length-3] + "..."
    return value


def _console_cols_to_fit(fields, data):
    cols, _ = shutil.get_terminal_size()
    data_sizes = []
    d = data[:]
    d.append(fields)
    for row in d:
        data_sizes.append(len(str(col)) for col in row)
    # print([x for x in (max(size) for size in zip(*data_sizes))])
    col_sizes = (max(size) for size in zip(*data_sizes))
    total_chars = 0
    for ndx, size in enumerate(col_sizes):
        total_chars += (size + 2)  # each column takes two extra chars
        # print(ndx, size, total_chars, cols)
        if total_chars > cols:
            return ndx - 1
    else:
        return len(fields)
