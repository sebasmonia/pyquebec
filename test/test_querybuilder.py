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
        # Monkeypatching - DataBase won't get the config from a file
        pyquebec.database.get_db_config = Mock()
        # Monkeypatching - Redirects schema_reader to the tests folder
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
        cls._db = test_db

    def test_ctor_nonedbinstance_then_raises_ValueError(self):
        self.assertRaises(ValueError, QueryBuilder,None)

    def test_ctor_validdbinstance_then_createavalidinstance(self):
        qb = QueryBuilder(self._db)
        self.assertIsNotNone(qb)

    def test_where_wherestring_then_appends_string(self):
        qb = QueryBuilder(self._db)
        qb.From(self._db.Album).where('1 = 1')
        query = qb.preview()
        expected = "SELECT * FROM Album  WHERE 1 = 1 "
        self.assertEqual(query, expected)

    def test_fromtable_where_wherestring_then_appends_string(self):
        qb = self._db.Album.From().where('1 = 1')
        query = qb.preview()
        expected = "SELECT * FROM Album  WHERE 1 = 1 "
        self.assertEqual(query, expected)

    def test_fromtable_where_wherestring_then_appends_string(self):
        qb = self._db.Album.From().where('1 = 1')
        query = qb.preview()
        expected = "SELECT * FROM Album  WHERE 1 = 1 "
        self.assertEqual(query, expected)

    def test_querybuilderorderby_columnorder(self):
        qb = QueryBuilder(self._db)
        qb.From(self._db.Album)
        qb.order_by(self._db.Album.Title,'ASC')
        query = qb.preview()
        expected = "SELECT * FROM Album   ORDER BY Album.Title ASC"
        self.assertEqual(query, expected)

    def test_querybuilderorderby_columnorder_three_calls(self):
        qb = QueryBuilder(self._db)
        qb.From(self._db.Album)
        qb.order_by(self._db.Album.Title,'ASC')
        qb.order_by(self._db.Album.AlbumId,'DESC')
        qb.order_by(self._db.Album.ArtistId,'ASC')
        query = qb.preview()
        expected = "SELECT * FROM Album   ORDER BY Album.Title ASC, Album.AlbumId DESC, Album.ArtistId ASC"
        self.assertEqual(query, expected)

    def test_querybuilder_inner_join_deductfields(self):
        qb = QueryBuilder(self._db)
        qb.From(self._db.Album)
        qb.inner_join(self._db.Artist)
        query = qb.preview()
        expected = "SELECT * FROM Album INNER JOIN Artist ON Album.ArtistId = Artist.ArtistId  "
        self.assertEqual(query, expected)

    def test_querybuilder_inner_join_explicitfields(self):
        qb = self._db.Album.From()
        qb.inner_join(self._db.Album.ArtistId, self._db.Artist.ArtistId)
        query = qb.preview()
        expected = "SELECT * FROM Album INNER JOIN Artist ON Album.ArtistId = Artist.ArtistId  "
        self.assertEqual(query, expected)

    def test_querybuilder_left_join_explicitfields(self):
        qb = self._db.Album.From()
        qb.left_join(self._db.Album.ArtistId, self._db.Artist.ArtistId)
        query = qb.preview()
        expected = "SELECT * FROM Album LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId  "
        self.assertEqual(query, expected)

    def test_querybuilder_inner_join_listpairs(self):
        qb = self._db.Track.From()
        join1 = (self._db.Track.GenreId, self._db.Genre.GenreId)
        join2 = (self._db.Album.AlbumId, self._db.Track.AlbumId)
        qb.inner_join((join1, join2))
        query = qb.preview()
        expected = "SELECT * FROM Track INNER JOIN Genre ON Track.GenreId = Genre.GenreId\nINNER JOIN Track ON Album.AlbumId = Track.AlbumId  "
        self.assertEqual(query, expected)


if __name__ == '__main__':
    unittest.main()

