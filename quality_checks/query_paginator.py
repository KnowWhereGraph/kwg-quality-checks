from typing import Callable

from SPARQLWrapper import JSON, QueryResult, SPARQLWrapper

from quality_checks.config import config


class QueryPaginator:
    """
    Class that takes care of retrieving all results for a query. This class can be used
    when querying data with more than 1,000 results as a way to avoid implementing a
    pagination system in the script.

    To use the class, pass the query and a function containing validation code to the
     `query` method. Internally, the function is called and the new page of results
      fed to it.
    """

    def __init__(self, limit=1000):
        """
        Creates a new Paginator

        :param limit: The maximum number of results to retrieve
        """
        if limit > 1000:
            raise ValueError(
                "The limit should be less than or equal to GraphDB's limit, of 1,000"
            )
        self.limit = limit

    def query(
        self,
        sparql_query: str,
        quality_check: Callable[[QueryResult.ConvertResult], None],
        offset: int = 0,
    ) -> None:
        """
        Queries the database, calling `quality_check` on each page. The callable
        function must contain unittest or general assert statements to trigger a
        test failure if a condition isn't met.

        def quality_check(query_results):
            # Example function that checks the results of a query
            assert query_results["results"]["bindings"][0]['count']['value'] == 100

        :param sparql_query: The SPARQL query being executed
        :param quality_check: A function that's run between
        paginations. The 'quality_check' parameter is a SPARQL ResultSet serialized as a
        python dict
        :param offset: The offset to start retrieving results from :return: None
        """
        # Add an offset and limit to the query
        sparql_query_limited = f"{sparql_query} OFFSET {offset} LIMIT {self.limit}"
        sparql = SPARQLWrapper(config.endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sparql_query_limited)
        query_results = sparql.query()
        converted = query_results.convert()
        if not isinstance(converted, dict):
            raise ValueError(
                f"Failed to get query results as a dict. {type(converted)}"
            )
        quality_check(converted)
        # If the length is equal to the maximum response length, query again,
        # increasing the offset by 1000
        if len(converted["results"]["bindings"]) == self.limit:
            self.query(sparql_query_limited, quality_check, offset + 1000)
        else:
            return
