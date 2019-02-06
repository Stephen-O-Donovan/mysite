import unittest
from utilities import *


class TestDatabase(unittest.TestCase):

    def setUp(self):
        pass

    def test_connection(self):
        #Test that a connection can be made to the database
        self.assertIsNotNone(create_connection())

    def test_queries(self):
        #Test that a response is recieved from queries
        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            result = cursor.fetchone()
            self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()