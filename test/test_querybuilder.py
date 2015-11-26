import unittest
from unittest.mock import Mock, MagicMock
from pyquebec.querybuilder import QueryBuilder
from pyquebec.dbobjects import Table

class TestQueryBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mock_db = Mock()
        mock_db.config = Mock()
        mock_db.config.uses_schema = True
        query_templates = {}
        query_templates['select'] = "SELECT {0}"
        query_templates['from'] = "FROM {0} WITH (NOLOCK)"
        query_templates['inner_join'] = "INNER JOIN {0} ON {1} = {2}"
        query_templates['left_join'] = "LEFT JOIN {0} ON {1} = {2}"
        query_templates['where'] = "WHERE {0}"
        query_templates['order_by'] = "ORDER BY {0}"
        mock_db.config.query_templates = query_templates
        mock_schema = Mock()
        mock_schema.schema_name = 'dbo'
        mock_db.dbo = mock_schema
        mock_table = Table(mock_db, mock_schema,'Table1',['Table1_id','Table1_description'])
        mock_db.dbo.Table1 = mock_table
        mock_table = Table(mock_db, mock_schema,'Table2',['Table2_id','Table2_description', 'Table1_id'])
        mock_db.foo.Table2 = mock_table
        cls._mock_db_instance = mock_db

    def test_querybuilderctor_nonedbinstance_then_raises_ValueError(self):
        self.assertRaises(ValueError, QueryBuilder,None)

    def test_querybuilderctor_validdbinstance_then_createavalidinstance(self):
        qb = QueryBuilder(self._mock_db_instance)
        self.assertIsNotNone(qb)

    # def test_querybuilderwhere_wherewithnone_then_raises_ValueError(self):
    #     qb = QueryBuilder(self._mock_db_instance)
    #     qb.From(self._mock_db_instance.foo.bar)
    #     self.assertRaises(ValueError, qb.where)

if __name__ == '__main__':
    unittest.main()

