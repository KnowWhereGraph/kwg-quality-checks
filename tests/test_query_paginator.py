import http.client as client
import socket
import unittest.mock
from unittest import TestCase, main, mock

import pytest
from SPARQLWrapper import QueryResult

from quality_checks.query_paginator import QueryPaginator


class QueryPaginatorTests(TestCase):
    """
    Tests that the paginator
        1. Calls the testing function
        2. Properly recurses over sparql pages
    """

    # Query result formats of different lengths
    return_pattern_half_page = {
        "head": {"vars": ["zip_area"]},
        "results": {
            "bindings": [
                {
                    "zip_area": {
                        "type": "uri",
                        "value": "http://stko-kwg.geog.ucsb.edu/lod/"
                        "resource/zipCodeArea.00646",
                    }
                }
            ]
            * 500
        },
    }
    return_pattern_full_page = {
        "head": {"vars": ["zip_area"]},
        "results": {
            "bindings": [
                {
                    "zip_area": {
                        "type": "uri",
                        "value": "http://stko-kwg.geog.ucsb.edu/lod/"
                        "resource/zipCodeArea.00646",
                    }
                }
            ]
            * 1000
        },
    }

    return_pattern_two_page = {
        "head": {"vars": ["zip_area"]},
        "results": {
            "bindings": [
                {
                    "zip_area": {
                        "type": "uri",
                        "value": "http://stko-kwg.geog.ucsb.edu/"
                        "lod/resource/zipCodeArea.00646",
                    }
                }
            ]
            * 2000
        },
    }

    def test_init(self) -> None:
        """
        Tests that the limit gets saved
        """
        limit = 100
        paginator = QueryPaginator(limit)
        self.assertEqual(paginator.limit, limit)

    @staticmethod
    def test_init_raises() -> None:
        """
        Tests that query limits over 1000 throw
        """
        with pytest.raises(ValueError):
            QueryPaginator(9000)

    @mock.patch("quality_checks.query_paginator.QueryResult.convert")
    @mock.patch("quality_checks.query_paginator.SPARQLWrapper.query")
    def test_passing_no_recursion(
        self, query_mock: unittest.mock.MagicMock, convert_mock: unittest.mock.MagicMock
    ) -> None:
        """
        Tests that when recursion isn't used, the correct number of results
        can be asserted

        :return: None
        """
        convert_mock.return_value = self.return_pattern_half_page
        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        query = """SELECT * WHERE { ?s ?p ?o }"""
        for page_results in QueryPaginator().query(query):
            self.assertEqual(len(page_results["results"]["bindings"]), 500)

    @mock.patch("quality_checks.query_paginator.QueryResult.convert")
    @mock.patch("quality_checks.query_paginator.SPARQLWrapper.query")
    def test_passing_recursion(
        self, query_mock: unittest.mock.MagicMock, convert_mock: unittest.mock.MagicMock
    ) -> None:
        """
        Tests that when there's more than one page of results, the paginator properly
        fetches each page.

        :return: None
        """
        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        # Return 2.5 pages of results
        convert_mock.side_effect = [
            self.return_pattern_full_page,
            self.return_pattern_full_page,
            self.return_pattern_half_page,
        ]
        query = """SELECT * WHERE { ?s ?p ?o FILTER(some_interesting_property)}"""

        self.assertEqual(len(list(QueryPaginator().query(query))), 3)

    @mock.patch("quality_checks.query_paginator.QueryResult.convert")
    @mock.patch("quality_checks.query_paginator.SPARQLWrapper.query")
    def test_failing_no_recursion(
        self, query_mock: unittest.mock.MagicMock, convert_mock: unittest.mock.MagicMock
    ) -> None:
        """
        Tests that failures can happen on non-recursive calls

        :return: None
        """
        # Only return 10 results, which should make the quality test function fail
        convert_mock.return_value = self.return_pattern_half_page
        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        query = """SELECT * WHERE { ?s ?p ?o }"""
        with pytest.raises(AssertionError):
            for page_results in QueryPaginator().query(query):
                # Pretend that we're expecting 1,000 results
                self.assertEqual(len(page_results), 1000)

    @mock.patch("quality_checks.query_paginator.QueryResult.convert")
    @mock.patch("quality_checks.query_paginator.SPARQLWrapper.query")
    def test_failing_recursion(
        self, query_mock: unittest.mock.MagicMock, convert_mock: unittest.mock.MagicMock
    ) -> None:
        """
        This test checks that if there's an error on a page after the first,
         the exception gets raised to pytest.

        :return: None
        """
        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        # Return 1.5 pages
        convert_mock.side_effect = [
            self.return_pattern_full_page,
            self.return_pattern_half_page,
        ]
        query = """SELECT * WHERE { ?s ?p ?o }"""
        with pytest.raises(AssertionError):
            for query_page in QueryPaginator().query(query):
                self.assertEqual(len(query_page), 1000)


if __name__ == "__main__":
    main()
