from typing import Dict, Generator, Any

from SPARQLWrapper import JSON, SPARQLWrapper

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
        offset: int = 0,
    ) -> Generator[Dict[Any, Any], None, None]:
        """
        Queries the database, returning a page of results
        :param sparql_query: The SPARQL query being executed
        :param offset: The offset to start retrieving results from :return: None
        :ret
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
        yield converted
        # If the length is equal to the maximum response length, query again,
        # increasing the offset by 1000
        if len(converted["results"]["bindings"]) == self.limit:
            self.query(sparql_query_limited, offset + 1000)
        else:
            return
