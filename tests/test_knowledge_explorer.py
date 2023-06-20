import unittest

from SPARQLWrapper import JSON, SPARQLWrapper

from quality_checks.config import config


class KnowledgeExplorerTests(unittest.TestCase):
    """
    Tests for sample queries in the Knowledge Explorer. These tests make up an early
    warning system for schema changes that effect the application.
    """

    def test_get_gnis_data(self) -> None:
        """
        The knowledge explorer makes use of several GNIS class types
        when constructing facets. This test ensures that there are
        a non-zero number of these classes in the database so that the
        ui controls are populated

        :return: None
        """
        for class_name in ["usgs:BuiltUpArea", "usgs:SurfaceWater", "usgs:Terrain"]:
            query = f"""
            PREFIX usgs: <http://gnis-ld.org/lod/usgs/ontology/>
            SELECT (count(?gnis_nodes) as ?count) WHERE {{
                ?gnis_nodes a {class_name} .
            }}
            """
            print(query)
            sparql = SPARQLWrapper(config.endpoint)
            sparql.setReturnFormat(JSON)
            sparql.setQuery(query)
            res = sparql.query().convert()
            # Assert that there's a non-zero number of gnis features
            print()
            self.assertGreater(
                int(res["results"]["bindings"][0]["count"]["value"]), 100
            )

    def test_experts_and_affiliations(self) -> None:
        """
        The knowledge explorer has a tab concerned with experts. This test checks
        to see if we have persons with expertise in the graph. If this fails,
        the 'peoples' tab won't function properly

        :return: None
        """
        # Query that counts the number of experts with expertise and locations
        query = """
        PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
        PREFIX iospress: <http://ld.iospress.nl/rdf/ontology/>

        SELECT (count(?entity) as ?count) {
         SELECT * WHERE {
          SELECT DISTINCT ?entity ?affiliation  ?affiliationLoc
            (group_concat(distinct ?expertise; separator = ", ") as ?expertise)
            WHERE {
              ?entity rdf:type iospress:Contributor.
              ?entity kwg-ont:hasExpertise ?expertise.
              ?entity iospress:contributorAffiliation ?affiliation.
              ?affiliation kwg-ont:sfWithin ?affiliationLoc.
              ?affiliationLoc rdf:type kwg-ont:AdministrativeRegion_3.
              } group by ?label ?entity ?affiliation ?affiliationLoc }
        }"""
        sparql = SPARQLWrapper(config.endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        res = sparql.query().convert()
        # Assert that there's some minimum number of experts
        self.assertGreater(int(res["results"]["bindings"][0]["count"]["value"]), 40)

    def test_has_country_states(self) -> None:
        """
        One of the KE dynamic facets works by constructing a list of
        administrative region hierarchies. If this test fails, the
        facet will fail to display options for administrative regions

        :return: None
        """
        query = """
        PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
        PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
        SELECT (count(?state) as ?count) WHERE {
            ?state kwg-ont:sfWithin kwgr:Earth.North_America.United_States.USA .
            ?state a kwg-ont:AdministrativeRegion_2 .
        }"""
        sparql = SPARQLWrapper(config.endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        res = sparql.query().convert()
        # Assert that there's 5 states, connected to the United States
        self.assertEqual(int(res["results"]["bindings"][0]["count"]["value"]), 50)


if __name__ == "__main__":
    unittest.main()
