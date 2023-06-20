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
        Tests that when recursion isn't used, the test function is called with
        the sparql results.

        :return: None
        """

        def quality_check(request_results):
            """
            A mock test that makes sure 500 entities were found
            """
            self.assertEqual(len(request_results["results"]["bindings"]), 500)

        convert_mock.return_value = self.return_pattern_half_page
        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        query = """SELECT * WHERE { ?s ?p ?o }"""
        QueryPaginator().query(query, quality_check)

    @mock.patch("quality_checks.query_paginator.QueryResult.convert")
    @mock.patch("quality_checks.query_paginator.SPARQLWrapper.query")
    def test_passing_recursion(
        self, query_mock: unittest.mock.MagicMock, convert_mock: unittest.mock.MagicMock
    ) -> None:
        """
        Tests that when there's more than one page of results, the paginator properly
        fetches each page. he test works by mocking the sparql requests and checking
        that the request functions are called the correct number of times (one time
        per page).

        :return: None
        """

        def quality_check(request_results: dict) -> None:
            """
            It's difficult to write a test that will pass when request_results
            will change between calls. Rather than test in this function, do nothing.
            """
            pass

        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        # Return 2.5 pages of results
        convert_mock.side_effect = [
            self.return_pattern_full_page,
            self.return_pattern_full_page,
            self.return_pattern_half_page,
        ]
        query = """SELECT * WHERE { ?s ?p ?o FILTER(some_interesting_property)}"""
        QueryPaginator().query(query, quality_check)
        # Check that convert() was called twice, testing that the second
        # page of values was retrieved
        self.assertEqual(convert_mock.call_count, 3)

    @mock.patch("quality_checks.query_paginator.QueryResult.convert")
    @mock.patch("quality_checks.query_paginator.SPARQLWrapper.query")
    def test_failing_no_recursion(
        self, query_mock: unittest.mock.MagicMock, convert_mock: unittest.mock.MagicMock
    ) -> None:
        """
        :return: None
        """

        def quality_check(request_results):
            """
            A mock test that checks if 1000 entities were found
            """
            self.assertEqual(len(request_results), 1000)

        # Only return 10 results, which should make the quality test function fail
        convert_mock.return_value = self.return_pattern_half_page
        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        query = """SELECT * WHERE { ?s ?p ?o }"""
        with pytest.raises(AssertionError):
            QueryPaginator().query(query, quality_check)

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

        def quality_check(request_results):
            """
            A mock test that checks if 1000 entities were found. This will pass the
            first time because a single page has 1000 results. It will fail the
            second, which will only have 500
            """
            self.assertEqual(len(request_results), 1000)

        query_mock.return_value = QueryResult(client.HTTPResponse(socket.socket()))
        # Return 1.5 pages
        convert_mock.side_effect = [
            self.return_pattern_full_page,
            self.return_pattern_half_page,
        ]
        query = """SELECT * WHERE { ?s ?p ?o }"""
        with pytest.raises(AssertionError):
            QueryPaginator().query(query, quality_check)


if __name__ == "__main__":
    main()
