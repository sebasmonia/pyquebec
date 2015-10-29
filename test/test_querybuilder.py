import unittest
from pyquebec.querybuilder import QueryBuilder

class TestQueryBuilder(unittest.TestCase):
    def test_where_with_None_value(self):
        self.assertRaises(ValueError, QueryBuilder,None)

if __name__ == '__main__':
    unittest.main()
