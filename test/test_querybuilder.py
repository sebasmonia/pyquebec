import unittest
from unittest.mock import Mock,MagicMock
from pyquebec.querybuilder import QueryBuilder
from pyquebec.dbobjects import Table

class TestQueryBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mock_db = Mock()
        mock_schema = Mock()
        mock_schema.schema_name = 'foo'
        mock_db.foo = mock_schema
        mock_table = Table(mock_db, mock_schema,'bar',['id','desc'])
        mock_db.foo.bar = mock_table   
        cls._mock_db_instance = mock_db

    def test_querybuilderctor_nonedbinstance_then_raises_ValueError(self):
        self.assertRaises(ValueError, QueryBuilder,None)

    def test_querybuilderctor_validdbinstance_the_createavalidinstance(self):
        qb = QueryBuilder(self._mock_db_instance)
        self.assertIsNotNone(qb)

    def test_querybuilderwhere_wherewithnone_then_raises_ValueError(self):
        qb = QueryBuilder(self._mock_db_instance)
        qb.From(self._mock_db_instance.foo.bar)
        self.assertRaises(ValueError, qb.where)

if __name__ == '__main__':
    unittest.main()

