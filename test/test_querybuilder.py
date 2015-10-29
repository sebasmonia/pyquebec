import unittest
from unittest.mock import Mock,MagicMock
from pyquebec.querybuilder import QueryBuilder

class TestQueryBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dbo_mock = Mock()
        cls._mock_db_instance = Mock()
        cls._mock_db_instance.dbo = MagicMock(return_value=dbo_mock)

    def test_querybuilderctor_nonedbinstance_then_raises_ValueError(self):
        self.assertRaises(ValueError, QueryBuilder,None)

    def test_querybuilderctor_validdbinstance_the_createavalidinstance(self):
        qb = QueryBuilder(self._mock_db_instance)
        self.assertIsNotNone(qb)
    
if __name__ == '__main__':
    unittest.main()
