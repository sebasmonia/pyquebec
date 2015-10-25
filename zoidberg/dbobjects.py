class Schema:
    def __init__(self, schema_name):
        self.schema_name = schema_name

    def tables(self):
        return {k: v for k, v in vars(self).items() if type(v) == Table}

    def table_finder(self, table_name, partial_name=True):
        table_name = table_name.lower()
        tables = self.tables().items()
        if partial_name:
            return [tbl for name, tbl in tables if table_name in name.lower()]
        else:
            matches = [tbl for name, tbl in tables
                       if table_name == name.lower()]
            if matches:
                return matches[0]  # Should be impossible to have more than one


class Table:
    def __init__(self, db_instance, schema, table_name, columns):
        self.schema = schema
        self.table_name = table_name
        self.db_instance = db_instance
        for col in columns:
            setattr(self, col, Column(self, col))

    def columns(self):
        return {k: v for k, v in vars(self).items() if type(v) == Column}

    def __str__(self):
        return self.schema.schema_name + "." + self.table_name

    def __repr__(self):
        return self.schema.schema_name + "." + self.table_name

    def From(self):
        q = self.db_instance.new_query().From(self)
        return q

    def inner_join(self, table2):
        q = self.db_instance.new_query().From(self).inner_join(table2)
        return q

    def left_join(self, table2):
        q = self.db_instance.new_query().From(self).left_join(table2)
        return q


class Column:
    def __init__(self, table, column_name):
        self.table = table
        self.column_name = column_name

    def __str__(self):
        return str(self.table) + "." + self.column_name

    def __repr__(self):
        return str(self.table) + "." + self.column_name

    def From(self):
        q = self.table.db_instance.new_query()
        q.From(self.table).select(self)
        return q

    def inner_join(self, field2):
        q = self.table.db_instance.new_query()
        q.inner_join((self, field2))
        return q

    def left_join(self, field2):
        q = self.table.db_instance.new_query()
        q.left_join((self, field2))
        return q
