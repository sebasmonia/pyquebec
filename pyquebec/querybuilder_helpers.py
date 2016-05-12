import sys
import shutil
import itertools

def field_picker(cols_getter, multi_select=True):
    all_cols = print_columns(cols_getter)
    if multi_select:
        sel = input("Provide a comma-separated list of colums (ex: 1,2,5,8):")
        sel = list(map(int, sel.split(',')))
        return [col for ndx, col in all_cols.items() if ndx in sel]
    else:
        sel = input("Select one column:")
        sel = int(sel)
        return all_cols[sel]

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
    all_cols = print_columns(qb_instance._all_columns_available)
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


def get_join_colums(table1, table2):
    t2_cols = table2.columns()
    t1_cols = table1.columns()
    matching_keys = set(t1_cols.keys()).intersection(t2_cols.keys())
    candidates = [(t1_cols[key], t2_cols[key]) for key in matching_keys]
    if len(candidates) > 1:
        print("Couldn't identify unique join column between",
                table1, table1, "- Pick a candidate or input blank to",
                "select between all columns:\n")
        single_list = [x[0].column_name for x in candidates]
        print_list([str(ndx) + "-" + row for ndx, row in enumerate(single_list, start=1)])
        sel = input()
        if sel != '':
            return candidates[int(sel) +1]
    print("Select the columns to use for the join between", table1.table_name, 'and', table2.table_name)
    print(table1.table_name, ":\n")
    col1 = field_picker(table1.columns().values, multi_select=False)
    print(table2.table_name, ":\n")
    col2 = field_picker(table2.columns().values, multi_select=False)
    return (col1, col2)


def print_columns(cols_getter):
    all_cols = {ndx: col for ndx, col in
                enumerate(cols_getter(), start=1)}
    text_to_print = [str(ndx) + "-" + col._query_repr() for ndx, col in all_cols.items()]
    print_list(text_to_print)
    return all_cols

def print_list(lst):
    max_width = max([len(s) for s in lst])
    terminal_width, _ = shutil.get_terminal_size()
    if terminal_width > 150 and (max_width * 3) < 150:
        print_3cols(lst)
    elif terminal_width > 100 and (max_width * 2) < 100:
        print_2cols(lst)
    else:
        print_1col(lst)
    print()

def print_3cols(foolist):
    for a,b,c in itertools.zip_longest(foolist[::3],foolist[1::3],foolist[2::3], fillvalue=''):
        print('{:<45}  {:<45}  {:<}'.format(a,b,c))

def print_2cols(foolist):
    for a,b in itertools.zip_longest(foolist[::2],foolist[1::2],fillvalue=''):
        print('{:<45}  {:<}'.format(a,b))

def print_1col(foolist):
    for a in foolist:
        print(a)