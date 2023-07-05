import json

import rdflib


class Config:
    """
    Class that abstracts the project configuration. It loads the config
    and exposes the contents as class properties.
    """

    def __init__(self) -> None:
        """
        Reads the application configuration
        """
        with open("config.json") as config_file:
            config_contents = json.load(config_file)
        self.endpoint: str = config_contents["endpoint"]
        self.namespaces = {}
        for namespace in config_contents["namespaces"]:
            self.namespaces.update(
                {namespace["prefix"]: rdflib.Namespace(namespace["uri"])}
            )

    def __str__(self) -> str:
        """
        Returns the config represented as a string

        :return: A dict representation of the config
        """
        return f"endpoint: {self.endpoint}" f"namespaces: {self.namespaces}"


# Use a pseudo singleton
config = Config()
