from django.test import TransactionTestCase, TestCase
from keyset_pagination.Paginator import KeysetPaginator
from keyset_pagination.models import KeySetModel
from django.db import connection


class IDPaginatorTestCase(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE keyset_pagination_keysetmodel;')
            cursor.execute('ALTER SEQUENCE keyset_pagination_keysetmodel_id_seq RESTART WITH 1;')
        self.inital_total = 25
        for i in range(1, self.inital_total+1):
            KeySetModel.objects.create(name=str(i))
        self.kp = KeysetPaginator(query_set=KeySetModel.objects.all(), per_page=5, reverse=False)

    def test_first_page(self):
        page = self.kp.page(None, None)
        self.assertEqual(page.last_id, 5)
        self.assertEqual(page.first_id, 1)
        self.assertEqual(page.has_previous(), False)
        self.assertEqual(page.has_next(), True)
        self.assertListEqual([1, 2, 3, 4, 5], [o.id for o in page])

    def test_scrolling(self):
        # second page
        page = self.kp.page(None, 5)
        self.assertListEqual([6, 7, 8, 9, 10], [o.id for o in page])
        self.assertEqual(page.last_id, 10)
        self.assertEqual(page.first_id, 6)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)
        # third page
        page = self.kp.page(None, 10)
        self.assertListEqual([11, 12, 13, 14, 15], [o.id for o in page])
        self.assertEqual(page.last_id, 15)
        self.assertEqual(page.first_id, 11)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)
        # fourth page
        page = self.kp.page(None, 15)
        self.assertListEqual([16, 17, 18, 19, 20], [o.id for o in page])
        self.assertEqual(page.last_id, 20)
        self.assertEqual(page.first_id, 16)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

    def test_scrolling_backwards(self):
        page = self.kp.page(21, None)
        self.assertListEqual([16, 17, 18, 19, 20], [o.id for o in page])
        self.assertEqual(page.last_id, 20)
        self.assertEqual(page.first_id, 16)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(16, None)
        self.assertListEqual([11, 12, 13, 14, 15], [o.id for o in page])
        self.assertEqual(page.last_id, 15)
        self.assertEqual(page.first_id, 11)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(11, None)
        self.assertListEqual([6, 7, 8, 9, 10], [o.id for o in page])
        self.assertEqual(page.last_id, 10)
        self.assertEqual(page.first_id, 6)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(6, None)
        self.assertListEqual([1, 2, 3, 4, 5], [o.id for o in page])
        self.assertEqual(page.last_id, 5)
        self.assertEqual(page.first_id, None)
        self.assertEqual(page.has_previous(), False)
        self.assertEqual(page.has_next(), True)

    def test_last_page(self):
        page = self.kp.page(None, 20)
        self.assertListEqual([21, 22, 23, 24, 25], [o.id for o in page])
        self.assertEqual(page.last_id, None)
        self.assertEqual(page.first_id, 21)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), False)

    def test_last_page_with_no_items(self):
        KeySetModel.objects.filter(id__gt=20).delete()
        page = self.kp.page(None, 20)

        self.assertListEqual([], list(page))
        self.assertEqual(page.last_id, None)
        self.assertEqual(page.first_id, None)
        self.assertEqual(page.has_previous(), False)
        self.assertEqual(page.has_next(), False)


class IDPaginatorReverseTestCase(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE keyset_pagination_keysetmodel;')
            cursor.execute('ALTER SEQUENCE keyset_pagination_keysetmodel_id_seq RESTART WITH 1;')
        self.inital_total = 25
        for i in range(1, self.inital_total+1):
            KeySetModel.objects.create(name=str(i))
        self.kp = KeysetPaginator(query_set=KeySetModel.objects.all(), per_page=5, reverse=True)

    def test_first_page(self):
        page = self.kp.page(None, None)
        self.assertEqual(page.last_id, 21)
        self.assertEqual(page.first_id, 25)
        self.assertEqual(page.has_previous(), False)
        self.assertEqual(page.has_next(), True)
        self.assertListEqual([25, 24, 23, 22, 21], [o.id for o in page])

    def test_scrolling(self):
        page = self.kp.page(None, 21)
        self.assertListEqual([20, 19, 18, 17, 16], [o.id for o in page])
        self.assertEqual(page.last_id, 16)
        self.assertEqual(page.first_id, 20)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(None, 16)
        self.assertListEqual([15, 14, 13, 12, 11], [o.id for o in page])
        self.assertEqual(page.last_id, 11)
        self.assertEqual(page.first_id, 15)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(None, 11)
        self.assertListEqual([10, 9, 8, 7, 6], [o.id for o in page])
        self.assertEqual(page.last_id, 6)
        self.assertEqual(page.first_id, 10)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

    def test_scrolling_backwards(self):
        page = self.kp.page(20, None)
        self.assertListEqual([25, 24, 23, 22, 21], [o.id for o in page])
        self.assertEqual(page.last_id, 21)
        self.assertEqual(page.first_id, None)
        self.assertEqual(page.has_previous(), False)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(15, None)
        self.assertListEqual([20, 19, 18, 17, 16], [o.id for o in page])
        self.assertEqual(page.last_id, 16)
        self.assertEqual(page.first_id, 20)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

        page = self.kp.page(10, None)
        self.assertListEqual([15, 14, 13, 12, 11], [o.id for o in page])
        self.assertEqual(page.last_id, 11)
        self.assertEqual(page.first_id, 15)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), True)

    def test_last_page(self):
        page = self.kp.page(None, 6)
        self.assertListEqual([5, 4, 3, 2, 1], [o.id for o in page])
        self.assertEqual(page.last_id, None)
        self.assertEqual(page.first_id, 5)
        self.assertEqual(page.has_previous(), True)
        self.assertEqual(page.has_next(), False)

