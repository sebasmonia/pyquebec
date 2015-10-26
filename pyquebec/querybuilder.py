from .dbobjects import Table, Column
import configparser
import sys

_config_file_path = __file__.replace(".py", ".ini")
_config = configparser.ConfigParser()
_config.optionxform = str
_config.read(_config_file_path)

_query_templates = {name: template for name, template in
                    _config['QueryTemplates'].items()}


class QueryBuilder():
    def __init__(self, db_instance):
        self.db_instance = db_instance
        self._values = {}
        self._values['select'] = '*'
        self._values['from'] = ''
        self._values['inner_join'] = []
        self._values['left_join'] = []
        self._values['where'] = ''
        self._values['order_by'] = []

    def clear_section(self, key):
        if key in ('inner_join', 'left_join', 'order_by'):
            self._values[key] = []
        elif key in ('from', 'where'):
            self._values[key] = ''
        elif key == 'select':
            self._values[key] = '*'
        else:
            print('Invalid section.')

    def preview(self):
        select = _query_templates['select']
        select = select.format(self._values['select'])
        From = _query_templates['from']
        From = From.format(self._values['from'])
        joins = []
        ij = _query_templates['inner_join']
        lj = _query_templates['left_join']
        for col1, col2 in self._values['inner_join']:
            joins.append(ij.format(col2.table, col1, col2))
        for col1, col2 in self._values['left_join']:
            joins.append(lj.format(col2.table, col1, col2))
        joins = '\n'.join(joins)
        if self._values['where']:
            where = _query_templates['where'].format(self._values['where'])
        else:
            where = ''
        if self._values['order_by']:
            s = ", ".join(str(col) + " " + sort for col, sort in
                          self._values['order_by'])
            order_by = _query_templates['order_by'].format(s)
        else:
            order_by = ''

        return ' '.join((select, From, joins, where, order_by))

    def From(self, *args):
        tables = self._resolve_table_arguments(args)
        if not tables:
            print('From: Invalid arguments')
            return
        self._values['from'] = tables[0]
        if len(tables) > 1:
            self.inner_join(*tables[1:])
        return self

    def _resolve_table_arguments(self, arguments):
        if len(arguments) == 1:
            arg = arguments[0]
            if type(arg) == str:
                return [self._find_table(arg)]
            if type(arg) == Table:
                return [arg]
            if type(arguments) == list:
                return arguments
        elif all(type(a) == Table for a in arguments):  # list of tables
            if type(arguments[0]) == Table:
                return list(arguments)
        else:
            return None

    def _find_table(self, str_name):
        str_name = str_name.lower()
        matches = [s.table_finder(str_name, partial_name=False) for s in
                   self.db_instance.schemas().values()]
        if any(matches):
            return [x for x in matches if x][0]

    def inner_join(self, *args):
        return self._create_join('inner_join', *args)

    def left_join(self, *args):
        return self._create_join('left_join', *args)

    def _create_join(self, join_type, *args):
        if (len(args) == 2 and type(args[0]) == Column and
           type(args[1]) == Column):  # two Column objects
            self._values[join_type].append(args)
        elif all((type(a) == tuple for a in args)):
            # assumes are all (col, col) tuples
            self._values[join_type].extend(args)
        else:  # analyze arguments like From
            new_tables = self._resolve_table_arguments(args)
            if not new_tables:
                print(join_type, ": Invalid arguments")
                return
            if not self._values['from']:
                self.From(new_tables[0])
                new_tables = new_tables[1:]
            main_table = self._values['from']
            fields = []
            for tbl in new_tables:
                f1f2 = self.identify_join_colums(main_table, tbl)
                if len(f1f2) != 1:
                    print("Couldn't identify unique join column between",
                          main_table, tbl, "- Candidates:",
                          (f1f2 if f1f2 else 'None'))
                    return  # aborts the call chaining
                fields.append(f1f2[0])
            else:  # will execute only if all fields were matched
                self._values[join_type].extend(fields)
        return self

    def identify_join_colums(self, table1, table2):
        t2_cols = table2.columns()
        t1_cols = table1.columns()
        matching_keys = set(t1_cols.keys()).intersection(t2_cols.keys())
        return [(t1_cols[key], t2_cols[key]) for key in matching_keys]

    def where(self, where_clause=None):
        if not where_clause:
            where_clause = self._where_builder()
        self._values['where'] = where_clause
        return self

    def order_by(self, *args):
        if not args:
            fields = self._field_picker()
            self._values['order_by'] = self._sort_order_by(fields)
        elif len(args) == 1 and type(args[0]) == str:
            self._values["order_by"].append((args[0], ''))
        elif (len(args) == 2 and type(args[0]) == Column and
              type(args[1]) == str):
            # assume Col object, "ASC" or "DESC"
            self._values["order_by"].append(args)
        elif all(len(tup) == 2 for tup in args):
            # expectation is list of tuples (Column, "ASC|DESC")
            self._values["order_by"].extend(args)
        else:
            print('order_by: Invalid arguments.')
            return
        return self

    def select(self, *args):
        fields = []
        if not args:
            fields = self._field_picker()
        elif (len(args) == 1 and type(args[0]) == list  # assume list of fields
              and all(type(a) == Column for a in args[0])):
            fields = args[0]
        elif all(type(a) == Column for a in args):  # each argument is a field
            fields = args
        else:
            print("select: Invalid argument(s)")
            return
        self._values['select'] = ', '.join(str(f) for f in fields)
        return self

    def _all_columns_available(self):
        tables = {self._values['from']}  # set, to avoid repeated tables
        both_joins = self._values['inner_join'] + self._values['left_join']
        for col1, col2 in both_joins:
            tables.add(col1.table)
            tables.add(col2.table)
        all_cols = []
        print(type(t) for t in tables)
        for tbl in tables:
            all_cols.extend(tbl.columns().values())
        return all_cols

    def _field_picker(self):
        all_cols = self._all_columns_available()
        for ndx, col in enumerate(all_cols, start=1):
            print(ndx, '-', str(col))
        sel = input("Provide a comma-separated list of colums (ex: 1,2,5,8):")
        sel = list(map(int, sel.split(',')))
        return [col for ndx, col in enumerate(all_cols, start=1) if ndx in sel]

    def _sort_order_by(self, fields):
        result = []
        print('For each field, indicate sort order: [A]sc or [D]esc.',
              'Defaults to Asc.')
        for col in fields:
            order = input('Field ' + str(col) + ': ASC or DESC? ')
            if order in ('D', 'd'):
                result.append((col, 'DESC'))
            else:
                result.append((col, 'ASC'))
        return result

    def _where_builder(self):
        all_cols = {ndx: col for ndx, col in
                    enumerate(self._all_columns_available(), start=1)}
        for ndx, col in all_cols.items():
            print(ndx, '-', str(col))
        msg = ("Provide the where clause. You can use {#} to refer to columns"
               " and {var_name} to refer to any variable in your "
               "environment (using format notation for list/dict elements\n")
        raw_where = input(msg)
        for ndx, col in all_cols.items():
            find_param = "{" + str(ndx) + "}"
            raw_where = raw_where.replace(find_param, str(col))
        main = sys.modules['__main__']
        return raw_where.format_map(vars(main))

    def go(self):
        s = self.preview()
        return self.db_instance.exec_query(s)

    def __str__(self):
        return self.preview()

    def __repr__(self):
        return self.preview()

    def clone(self):
        the_clone = QueryBuilder(self.db_instance)
        the_clone._values['select'] = self._values['select']
        the_clone._values['from'] = self._values['from']
        the_clone._values['inner_join'] = self._values['inner_join']
        the_clone._values['left_join'] = self._values['left_join']
        the_clone._values['where'] = self._values['where']
        the_clone._values['order_by'] = self._values['order_by']
        return the_clone()
