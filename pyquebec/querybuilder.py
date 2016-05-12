from . import querybuilder_helpers as qbhelpers
from . import formatters

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
        self._values['from'] = []
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
        self._values['from'] = args[0]
        if len(args) > 1:
            self.inner_join(*args[1:])
        return self

    def inner_join(self, *args):
        return self._create_join('inner_join', *args)

    def left_join(self, *args):
        return self._create_join('left_join', *args)

    def _create_join(self, join_type, *args):
        if not self._values['from']:
            self.From(args[0])
            new_tables = args[1:]
        else:
            new_tables = args
        main_table = self._values['from']
        fields = []
        for tbl in new_tables:
            f1f2 = qbhelpers.get_join_colums(main_table, tbl)
            fields.append(f1f2)
        else:
            self._values[join_type].extend(fields)
        return self

    def where(self, where_clause=None, vars_map=None):
        if not where_clause:
            where_clause = qbhelpers.where_builder(self, vars_map)
        self._values['where'] = where_clause
        return self

    def order_by(self, *args):
        if not args:
            fields = qbhelpers.field_picker(self._all_columns_available)
            self._values['order_by'] = qbhelpers.sort_order_by(fields)
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
            fields = qbhelpers.field_picker(self._all_columns_available)
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

    def go(self):
        s = self.preview()
        return self.db_instance.exec_sql(s)

    def go_html(self):
        results = self.go()
        formatters.to_html(results)

    def go_csv(self):
        results = self.go()
        formatters.to_csv(results)

    def go_console(self):
        results = self.go()
        formatters.to_console(results)

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
