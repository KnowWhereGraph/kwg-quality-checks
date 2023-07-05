from unittest import TestCase, mock

import rdflib


class ConfigTests(TestCase):
    """
    Unit tests for the Config class
    """

    @mock.patch("builtins.open")
    def test_namespace_construction(self, open_patch: mock.MagicMock) -> None:
        """
        Ensures that the config ALWAYS creates rdflib.Namespace objects out of the
        prefixes defined in the file.

        :return: None
        """
        mock_config = {
            "endpoint": "httstaging.knowwheregraph.org/sparql",
            "namespaces": [
                {
                    "uri": "http://stko-kwg.geog.ucsb.edu/lod/resource/",
                    "prefix": "kwgr",
                },
                {
                    "uri": "http://stko-kwg.geog.ucsb.edu/lod/ontology/",
                    "prefix": "kwgo",
                },
            ],
        }

        with mock.patch("json.load", mock.MagicMock()) as mock_file:
            mock_file.return_value = mock_config

            # Import the config now that the opening & reading has been mocked
            from quality_checks.config import config

            self.assertEqual(
                config.namespaces["kwgr"],
                rdflib.Namespace("http://stko-kwg.geog.ucsb.edu/lod/resource/"),
            )
            self.assertEqual(
                config.namespaces["kwgo"],
                rdflib.Namespace("http://stko-kwg.geog.ucsb.edu/lod/ontology/"),
            )
