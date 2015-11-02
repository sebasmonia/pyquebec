"""Assortment of helpers to print\manipulate data
"""
import tempfile
import os
import csv
import shutil
import configparser
from tabulate import tabulate

_config_file_path = __file__.replace(".py", ".ini")
_config = configparser.ConfigParser()
_config.read(_config_file_path)
_html_options = _config["HTMLOptions"]
_console_options = _config["ConsoleOptions"]


def to_html(data):
    if not data:
        return
    fields, formatter = _deduct_fields_formatter(data[0])
    row_template = ('<tr>' + ''.join("<td>{" + f + "}</td>"
                    for f in fields) + '</tr>')
    header_footer_text = ''.join("<th>" + f + "</th>" for f in fields)

    mark_up = ["""<TABLE id="tbResultSet" class="display" cellspacing="0"
               width="100%">"""]
    mark_up.append('<thead><TR>')
    mark_up.append(header_footer_text)
    mark_up.append('</TR></thead>')
    mark_up.append('<tfoot><TR>')
    mark_up.append(header_footer_text)
    mark_up.append('</TR></tfoot>')
    mark_up.append('<tbody>')
    for row in data:
        mark_up.append(row_template.format_map(formatter(row)))
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


def _deduct_fields_formatter(sample):
    """
    Extracts the header/fields from the collection, and the function used to
    retrieve the information from each element
    """
    # this function is called after validation of at least one row present
    fields = None
    func = None

    if type(sample) == dict:
        fields = tuple(sample.keys())
        func = lambda elem: elem  # identity
    if isinstance(sample, tuple) and hasattr(sample, '_fields'):
        fields = sample._fields  # named tuple
        func = lambda elem: elem._asdict()
    if type(sample) in (list, tuple):
        fields = tuple("C" + str(n) for n in range(len(sample)))
        func = lambda elem: dict(enumerate(elem))

    return fields, func


def to_csv(data):
    if not data:
        return
    fields, formatter = _deduct_fields_formatter(data[0])
    csvfile_handle, csvpath = tempfile.mkstemp(".csv", text=True)
    print("Creating and opening temp file", csvpath)
    with os.fdopen(csvfile_handle, mode="w", encoding="UTF-8",
                   newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(formatter(row))
    os.startfile(csvpath)


def to_console(data):
    if not data:
        return
    fields, dict_converter = _deduct_fields_formatter(data[0])
    fields = [_console_column_formatter(f) for f in fields]
    col_count = _console_cols_to_fit()
    # a copy of the data, pre-formatted
    formatted_data = []
    for d in map(dict_converter, data):
        tup = tuple(map(_console_column_formatter, d.values()))[:col_count]
        formatted_data.append(tup)
    console_text = tabulate(formatted_data, headers=fields)
    print(console_text)


def _console_column_formatter(value):
    value = str(value)
    max_length = int(_console_options['Max_Col_Length'])
    if len(value) > max_length:
        value = value[:max_length-3] + "..."
    return value


def _console_cols_to_fit():
    cols, _ = shutil.get_terminal_size()
    max_length = int(_console_options['Max_Col_Length'])
    return cols // max_length
