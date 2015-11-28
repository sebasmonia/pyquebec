import unittest
from unittest.mock import Mock, MagicMock
from pyquebec.querybuilder import QueryBuilder
import os
import pyquebec.database
import pyquebec.schema_reader as schema_reader
import pyquebec

class TestQueryBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyquebec.database.get_db_config = Mock()
        schema_reader._cache_folder = os.path.split(__file__)[0]
        test_schema = pyquebec.schema_reader.read_schema_from_cache('Chinook_Test')
        test_db = pyquebec.database.DataBase('Test', test_schema)
        test_db.config = Mock()
        test_db.config.uses_schema = False
        test_db.db_name = 'Test'
        query_templates = {}
        query_templates['select'] = "SELECT {0}"
        query_templates['from'] = "FROM {0}"
        query_templates['inner_join'] = "INNER JOIN {0} ON {1} = {2}"
        query_templates['left_join'] = "LEFT JOIN {0} ON {1} = {2}"
        query_templates['where'] = "WHERE {0}"
        query_templates['order_by'] = "ORDER BY {0}"
        test_db.config.query_templates = query_templates
        cls._test_db = test_db

    def test_querybuilderctor_nonedbinstance_then_raises_ValueError(self):
        self.assertRaises(ValueError, QueryBuilder,None)

    def test_querybuilderctor_validdbinstance_then_createavalidinstance(self):
        qb = QueryBuilder(self._test_db)
        self.assertIsNotNone(qb)

    def test_querybuilderwhere_wherestring_then_appends_string(self):
        qb = QueryBuilder(self._test_db)
        qb.From(self._test_db.Album).where('1 = 1')
        query = qb.preview()
        expected = "SELECT * FROM Album  WHERE 1 = 1 "
        self.assertEqual(query, expected)

    def test_querybuilder_fromtable_where_wherestring_then_appends_string(self):
        qb = self._test_db.Album.From().where('1 = 1')
        query = qb.preview()
        expected = "SELECT * FROM Album  WHERE 1 = 1 "
        self.assertEqual(query, expected)

    # def test_querybuilderwhere_wherewithnone_then_raises_ValueError(self):
    #     qb = QueryBuilder(self._mock_db_instance)
    #     qb.From(self._mock_db_instance.foo.bar)
    #     self.assertRaises(ValueError, qb.where)

if __name__ == '__main__':
    unittest.main()

