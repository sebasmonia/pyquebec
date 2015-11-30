import unittest
from unittest.mock import Mock, MagicMock
from pyquebec.dbobjects import Table, Column
import os
import pyquebec.database
import pyquebec.schema_reader as schema_reader
import pyquebec

class TestQueryBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Monkeypatching - DataBase won't get the config from a file
        pyquebec.database.get_db_config = Mock()
        # Monkeypatching - Redirects schema_reader to the tests folder
        schema_reader._cache_folder = os.path.split(__file__)[0]
        test_schema = pyquebec.schema_reader.read_schema_from_cache('Chinook_Test')
        test_db = pyquebec.database.DataBase('Test', test_schema)
        test_db.config = Mock()
        test_db.config.uses_schema = False
        test_db.db_name = 'Test'
        cls._db = test_db

    def test_table_queryrepr(self):
        tbl = self._db.Album
        qrepr = tbl._query_repr()
        expected = "Album"
        self.assertEqual(qrepr, expected)

    def test_column_queryrepr(self):
        col = self._db.Artist.ArtistId
        qrepr = col._query_repr()
        expected = "Artist.ArtistId"
        self.assertEqual(qrepr, expected)

# import unittest
# from unittest.mock import Mock, MagicMock
# import pyquebec.dbobjects as dbobjects
# import os
# import pyquebec.database
# import pyquebec.schema_reader as schema_reader
# import pyquebec

# class TestQueryBuilder(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         mock_db = Mock()
#         mock_db.db_name = 'TestDB'
#         schema = dbobjects.Schema('TestSchema')
#         table1 = dbobjects.Table(mock_db, schema, 'Table1', ['Col11', 'Col12', 'Col13'])
#         table2 = dbobjects.Table(mock_db, schema, 'Table2', ['Col21', 'Col22', 'Col23'])
#         table3 = dbobjects.Table(mock_db, schema, 'Table3', ['Col31', 'Col32', 'Col33'])
#         cls._db = mock_db
#         cls._tables = { 'Table1': table1, 'Table2': table2, 'Table3': table3 }

#     def test_table_queryrepr(self):
#         tbl = self._db.TestSchema.Table1
#         qrepr = tbl._query_rpr()
#         expected = "TestSchema.Table1"
#         self.assertEqual(correct)