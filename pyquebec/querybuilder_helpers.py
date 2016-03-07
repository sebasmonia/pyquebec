import sys


def field_picker(qb_instance):
    all_cols = qb_instance._all_columns_available()
    for ndx, col in enumerate(all_cols, start=1):
        print(ndx, '-', col._query_repr())
    sel = input("Provide a comma-separated list of colums (ex: 1,2,5,8):")
    sel = list(map(int, sel.split(',')))
    return [col for ndx, col in enumerate(all_cols, start=1) if ndx in sel]


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


def where_builder(qb_instance):
    all_cols = {ndx: col for ndx, col in
                enumerate(qb_instance._all_columns_available(), start=1)}
    for ndx, col in all_cols.items():
        print(ndx, '-', col._query_repr())
    msg = ("Provide the where clause. You can use {#} to refer to columns"
            " and {var_name} to refer to any variable in your "
            "environment (using format notation for list/dict elements)\n")
    raw_where = input(msg)
    for ndx, col in all_cols.items():
        find_param = "{" + str(ndx) + "}"
        raw_where = raw_where.replace(find_param, col._query_repr())
    main = sys.modules['__main__']
    return raw_where.format_map(vars(main))
