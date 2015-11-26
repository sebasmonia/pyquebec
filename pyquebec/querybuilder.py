import sys


class QueryBuilder():

    def __init__(self, db_instance):
        if db_instance is None:
            raise ValueError("QueryBuilder must be initialized with "
                             "a valid DataBase instance")
        templates = db_instance.config.query_templates
        self._query_templates = {name: temp for name, temp in
                                 templates.items()}
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
        select = self._query_templates['select']
        select = select.format(self._values['select'])
        From = self._query_templates['from']
        From = From.format(self._values['from']._query_repr())
        joins = []
        ij = self._query_templates['inner_join']
        lj = self._query_templates['left_join']
        for col1, col2 in self._values['inner_join']:
            joins.append(ij.format(col2.table._query_repr(),
                                   col1._query_repr(),
                                   col2._query_repr()))
        for col1, col2 in self._values['left_join']:
            joins.append(lj.format(col2.table._query_repr(),
                                   col1._query_repr(),
                                   col2._query_repr()))
        joins = '\n'.join(joins)
        if self._values['where']:
            where = self._query_templates['where']
            where = where.format(self._values['where'])
        else:
            where = ''
        if self._values['order_by']:
            s = ", ".join(col._query_repr() + " " + sort for col, sort in
                          self._values['order_by'])
            order_by = self._query_templates['order_by'].format(s)
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
            if QueryBuilder._is_db_obj(arg):
                return [arg]  # comes from dbobject
            if type(arg) == str:
                return [self._find_table(arg)]
            if type(arguments) == list:
                return arguments
        elif all(QueryBuilder._is_db_obj(a) for a in arguments):
            # list of dbobj
            return list(arguments)
        else:
            return None

    def _find_table(self, str_name):
        str_name = str_name.lower()
        matches = self.db_instance.table_finder(str_name, partial_name=False)
        if matches:
            return [x for x in matches if x][0]
        else:
            raise ValueError("Not a valid table name")

    def inner_join(self, *args):
        return self._create_join('inner_join', *args)

    def left_join(self, *args):
        return self._create_join('left_join', *args)

    def _create_join(self, join_type, *args):
        is_db = QueryBuilder._is_db_obj
        if (len(args) == 2 and is_db(args[0]) and
           is_db(args[1])):  # two Column objects
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
        elif (len(args) == 2 and QueryBuilder._is_db_obj(args[0]) and
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
        elif (len(args) == 1 and type(args[0]) == list  # assume list of Cols
              and all(QueryBuilder._is_db_obj(a) for a in args[0])):
            fields = args[0]
        elif all(QueryBuilder._is_db_obj(a) for a in args):
            # each argument is a field
            fields = args
        else:
            print("select: Invalid argument(s)")
            return
        self._values['select'] = ', '.join(f._query_repr() for f in fields)
        return self

    def _all_columns_available(self):
        tables = {self._values['from']}  # set, to avoid repeated tables
        both_joins = self._values['inner_join'] + self._values['left_join']
        for col1, col2 in both_joins:
            tables.add(col1.table)
            tables.add(col2.table)
        all_cols = []
        for tbl in tables:
            all_cols.extend(tbl.columns().values())
        return all_cols

    def _field_picker(self):
        all_cols = self._all_columns_available()
        for ndx, col in enumerate(all_cols, start=1):
            print(ndx, '-', col._query_repr())
        sel = input("Provide a comma-separated list of colums (ex: 1,2,5,8):")
        sel = list(map(int, sel.split(',')))
        return [col for ndx, col in enumerate(all_cols, start=1) if ndx in sel]

    def _sort_order_by(self, fields):
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

    def _where_builder(self):
        all_cols = {ndx: col for ndx, col in
                    enumerate(self._all_columns_available(), start=1)}
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
        return the_clone

    @staticmethod
    def _is_db_obj(obj):
        return hasattr(obj, "_query_repr")
