import sys
import shutil
import itertools

def field_picker(qb_instance):
    all_cols = print_columns(qb_instance)
    sel = input("Provide a comma-separated list of colums (ex: 1,2,5,8):")
    sel = list(map(int, sel.split(',')))
    return [col for ndx, col in all_cols.items() if ndx in sel]

def sort_order_by(fields):
    result = []
    print('For each field, indicate sort order: [A]sc or [D]esc.',
            'Defaults to Asc.')
    for col in fields:
        order = input('Field ' + col._query_repr() + ': ASC or DESC? ')
        if order in ('D', 'd'):
            result.append((col, 'DESC'))
        else:
            result.append((col, 'ASC'))
    return result


def where_builder(qb_instance, vars_map=None):
    all_cols = print_columns(qb_instance)
    msg = ("Provide the where clause. You can use {#} to refer to columns"
            " and {var_name} to refer to any variable in your "
            "environment (using format notation for list/dict elements)\n")
    raw_where = input(msg)
    for ndx, col in all_cols.items():
        find_param = "{" + str(ndx) + "}"
        raw_where = raw_where.replace(find_param, col._query_repr())
    if not vars_map:
        main = sys.modules['__main__']
        vars_map = vars(main)
    return raw_where.format_map(vars_map)

def print_columns(qb_instance):
    all_cols = {ndx: col for ndx, col in
                enumerate(qb_instance._all_columns_available(), start=1)}
    text_to_print = [str(ndx) + "-" + col._query_repr() for ndx, col in all_cols.items()]
    terminal_width, _ = shutil.get_terminal_size()
    if terminal_width > 150:
        print_3cols(text_to_print)
    elif terminal_width > 100:
        print_2cols(text_to_print)
    else:
        print_1col(text_to_print)
    print()
    return all_cols

def print_3cols(foolist):
    for a,b,c in itertools.zip_longest(foolist[::3],foolist[1::3],foolist[2::3], fillvalue=''):
        print('{:<45}  {:<45}  {:<}'.format(a,b,c))

def print_2cols(foolist):
    for a,b in itertools.zip_longest(foolist[::2],foolist[1::2],fillvalue=''):
        print('{:<45}  {:<}'.format(a,b))

def print_1col(foolist):
    for a in foolist:
        print(a)