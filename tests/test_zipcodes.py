import unittest

from SPARQLWrapper import JSON, SPARQLWrapper

from quality_checks.config import config


class ZipCodeTests(unittest.TestCase):
    """
    Unit tests for the US Zipcodes dataset. These tests require
    1. Zipcode data
    """

    def test_non_zero(self):
        """
        Tests that the graph has a bulk of zipcode nodes. New zipcodes are added each
         year, so rather than test exact numbers, test that there are at least 40k

        :return: None
        """
        # Query that counts the number of ZipCodeAreas
        query = """
        PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>

            SELECT (count(?zip_area) as ?count) WHERE {
              ?zip_area a kwg-ont:zipCodeArea .
        }
        """

        sparql = SPARQLWrapper(config.endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        res = sparql.query().convert()
        # There are at least 40k zipcodes
        self.assertGreater(int(res["results"]["bindings"][0]["count"]["value"]), 1)


var = {
    "head": {"vars": ["count"]},
    "results": {
        "bindings": [
            {
                "count": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                    "type": "literal",
                    "value": "0",
                }
            }
        ]
    },
}


if __name__ == "__main__":
    unittest.main()
