#!/usr/bin/env python
# encoding: utf-8
"""
test_searcher.py
"""
from __future__ import absolute_import

import os
import six
from . import testcase
from core.sherlock import indexer, searcher
from core.utils import debug


class TestSearcher(testcase.BaseTestCase):
    def setUp(self):
        """ Called before each test """
        testcase.BaseTestCase.setUp(self)

    def tearDown(self):
        """ Called after each test """

    def test_simple_search(self):
        """Tests simple search logic
        """
        # index a file for the search
        path = os.path.join(self.test_dir, six.u('text/objc_example.m'))
        idxr = indexer.get_indexer(name='test', rebuild_index=True)
        idxr.index_text(path)
        # test values
        self.assertTrue(idxr.doc_count() == 1, 'bad doc count, expected 1 but, found %d' % idxr.doc_count())

        idx = idxr.get_index()
        # find something in the file
        results = idx.search(six.u('key'))
        self.assertTrue(len(results) == 1, 'wrong hit count, expected 1 but, found %d' % len(results))

    def test_simple_unicode_search(self):
        """Tests simple search logic using a unicode string
        """
        # index a file for the search
        path = os.path.join(self.test_dir, six.u('text/example.py'))
        idxr = indexer.get_indexer(name='test', rebuild_index=True)
        idxr.index_text(path)
        # test values
        self.assertTrue(idxr.doc_count() == 1, 'bad doc count, expected 1 but, found %d' % idxr.doc_count())

        idx = idxr.get_index()
        # find some unicode in the file
        results = idx.search(six.u('©opyright'))
        self.assertTrue(len(results) == 1, 'wrong hit count, expected 1 but, found %d' % len(results))

    def test_search(self):
        """Tests searching against more than one document
        """
        # index directory
        idxr = indexer.get_indexer(name='test', rebuild_index=True)
        path = os.path.join(self.test_dir, six.u('text'))
        idxr.index_text(path)
        self.assertTrue(idxr.doc_count() == 7, "Bad document index count, expected 7 but, indexed %d" % idxr.doc_count())
        # search
        idx = idxr.get_index()
        search_text = six.u('value')
        results = idx.search(search_text)
        self.assertTrue(len(results) > 1, 'not enough results from the search, expected more than 1, but found %d' % len(results))
        # search by path
        results = idx.search_path(os.path.join(path, six.u('objc_example.m')))
        self.assertTrue(len(results) == 1, 'wrong number of results for the path search, expected 1, but found %d' % len(results))


def run():
    return testcase.run_all(TestSearcher)
