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

