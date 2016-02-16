"""Assortment of helpers to print/manipulate data."""
import tempfile
import os
import csv
import shutil
from .config import get_config_section

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

    headers = data[0]._fields
    formatted_headers = { f:_console_column_formatter(f) for f in headers }
    formatted_data = []
    for elem in data:
        formatted = { key: _console_column_formatter(val) for key, val in elem._asdict().items() }
        formatted_data.append(formatted)
    col_lenghts, cols_to_display = _console_cols_to_fit(headers,formatted_headers, formatted_data)
    format_strings = { h: "{:^" + str(col_lenghts[h]) + "}" for h in headers }
    for h in headers[:cols_to_display]:
        print((format_strings[h]).format(formatted_headers[h]), end= "|")
    print()
    for h in headers[:cols_to_display]:
        print('-' * col_lenghts[h],end= "|")
    print()
    for row in formatted_data:
        for h in headers[:cols_to_display]:
            print((format_strings[h]).format(row[h]), end= "|")
        print()
    if cols_to_display < len(headers):
        print("\n", cols_to_display, "out of", len(headers), " columns visible.")

def _console_column_formatter(value):
    value = str(value)
    max_length = int(_console_options['Max_Col_Length'])
    if len(value) > max_length:
        value = value[:max_length-3] + "..."
    return value


def _console_cols_to_fit(headers, formatted_headers, data):
    col_lenghts = {}
    for h in headers:
        lenght = max([len(x[h]) for x in data])
        col_lenghts[h] = lenght

    # check if header is wider than data
    for k, v in col_lenghts.items():
        if len(formatted_headers[k]) > v:
            col_lenghts[k] = len(formatted_headers[k])

    total_chars, _ = shutil.get_terminal_size()
    chars_count = 1 # accounts for final EOL char
    for col_index, col_name in enumerate(headers):
        chars_count += (col_lenghts[col_name] + 1)  # each column takes one extra char
        if chars_count > total_chars:
            return col_lenghts, col_index

    else:
        return col_lenghts, len(headers)
