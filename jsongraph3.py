#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""JSON Graph Python Library

Parameters
----------
None

Returns
-------
None

Long Description
"""

import logging
import io
import json
import os.path
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

from jsonschema import Draft4Validator
# from objects.edge import Edge
# from objects.graph import Graph
# from objects.multigraph import Multigraph
# from objects.node import Node  # TODO add in original


logger = logging.getLogger(__name__)


def load_json_string(jsonstring):
    """Check if string is JSON and if so return python dictionary"""

    try:
        json_object = json.loads(jsonstring)
    except ValueError as e:
        return False
    return json_object


def get_github_masterschema():
    """Read JSON Graph Schema file from Github Master branch"""
    link = "https://raw.githubusercontent.com/jsongraph/json-graph-specification/master/json-graph-schema_v2.json"
    f = urllib.request.urlopen(link)
    js = json.load(f)
    f.close

    return js


def get_json(jsongraph):
    """Check if parameter is a file object, filepath or JSON string

        Return:  dictionary object OR False for failure
    """
    if type(jsongraph) is dict:
        return jsongraph
    elif isinstance(jsongraph, io.IOBase):
        return json.load(jsongraph)
    elif os.path.isfile(jsongraph):
        with open(jsongraph, "rb") as f:
            return json.load(f)

    jg = load_json_string(jsongraph)
    if jg:
        return jg
    else:
        return False


def validate_schema(schema="", verbose=False):
    """Validate schema file"""

    if not schema:
        schema = get_github_masterschema()
    else:
        schema = get_json(schema)

    results = Draft4Validator.check_schema(schema)

    if verbose and results:
        print("    Schema doesn't validate!")
        print(results)
    elif verbose:
        print("    Schema Validates!")

    if results:
        return (False, results)

    return (True, "")


def validate_jsongraph(jsongraph, schema="", verbose=False):
    """Validate JSON Graph against given jsongraph object and schema object"""

    jg = get_json(jsongraph)

    if not schema:
        schema = get_github_masterschema()
    else:
        schema = get_json(schema)

    if not jg:
        sys.exit(
            "JSON Graph parameter does not appear to be a file object, filepath or JSON string."
        )
    if not schema:
        sys.exit(
            "JSON Graph Schema parameter does not appear to be a file object, filepath or JSON string."
        )

    schema = Draft4Validator(schema)  # transform schema in a Schema validation object

    errors = []
    for error in schema.iter_errors(jg):
        logging.error(error)
        errors.append(error)

    status = len(errors) == 0
    return status, errors


def load_graphs(jsongraphs, validate=False, schema="", verbose=False):
    """Loads one or more graphs from jsongraphs JSON as a generator"""

    jgs = get_json(jsongraphs)

    if validate:
        success, results = validate_jsongraph(jsongraphs, schema, verbose)
        if not success:
            raise TypeError("JSON Graph does not validate")

    if "graph" in jgs:
        yield jgs["graph"]

    if "graphs" in jgs:
        for graph in jgs["graphs"]:
            yield graph


def test_example_graphs():
    """Test and usage example"""
    single_graph_link = "https://raw.githubusercontent.com/jsongraph/json-graph-specification/master/examples/usual_suspects.json"
    multiple_graph_link = "https://raw.githubusercontent.com/jsongraph/json-graph-specification/master/examples/car_graphs.json"

    f = urllib.request.urlopen(single_graph_link)
    sg = json.load(f)
    f.close

    f = urllib.request.urlopen(multiple_graph_link)
    mg = json.load(f)
    f.close

    print("Does JSON Graph Schema validate?")
    validate_schema(schema="", verbose=True)

    print("\nDoes Single Graph example validate?")
    validate_jsongraph(sg, schema="", verbose=True)

    print("\nShow Label of Single Graph")
    graphs = load_graphs(sg, validate=False, schema="", verbose=False)
    print("    Label: ", next(graphs)["label"])

    print("\nShow Label's of Multiple Graphs")
    graphs = load_graphs(mg, validate=False, schema="", verbose=False)
    for graph in graphs:
        print("    Label: ", graph["label"])


def main():
    test_example_graphs()


if __name__ == "__main__":
    main()
