#!/usr/bin/env/python

"""
    datasets-rdf.py -- Read jkan dataset files and make VIVO RDF

jkan dataset format is :

title: TITLE
organization: ORGANIZATION
notes: NOTES
resources:
  - name: NAME1
    url: URL1
    format: FORMAT1
  - name: NAME2
    url: URL2
    format: FORMAT2
category:
  - CATEGORY1
  - CATEGORY2
maintainer: MAINTAINER_NAME
maintainer_email: MAINTAINER_EMAIL
author: AUTHOR_NAME
author_email: AUTHOR_EMAIL

as json:

{
  "title": "TITLE",
  "organization": "ORGANIZATION",
  "notes": "NOTES",
  "resources": [
    {
      "name": "NAME1",
      "url": "URL1",
      "format": "FORMAT1"
    },
    {
      "name": "NAME2",
      "url": "URL2",
      "format": "FORMAT2"
    }
  ],
  "category": [
    "CATEGORY1",
    "CATEGORY2"
  ],
  "maintainer": "MAINTAINER_NAME",
  "maintainer_email": "MAINTAINER_EMAIL",
  "author": "AUTHOR_NAME",
  "author_email": "AUTHOR_EMAIL",
  "basename": "BASENAME"
}

"""

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDFS, RDF, XSD
import logging
import json
import os
from pprint import pprint

__author__    = "Paul Friedman"
__license__   = "Apache License 2.0"
__version__   = "0.01"

# Constants
VIVO    = Namespace('http://vivoweb.org/ontology/core#')
FOAF    = Namespace('http://xmlns.com/foaf/0.1/')
OBO     = Namespace('http://purl.obolibrary.org/obo/')
VCARD   = Namespace('http://www.w3.org/2006/vcard/ns#')
OWL     = Namespace('http://www.w3.org/2002/07/owl#')
DCAT    = Namespace('http://www.w3.org/ns/dcat#')
VLOCAL  = Namespace('http://vivo.northwestern.edu/ontology/vlocal#')
DCTERMS = Namespace('http://purl.org/dc/terms/')

dataset_prefix = 'http://vivo.northwestern.edu/individual/n_dcat_dataset_'
vcard_prefix   = 'http://vivo.northwestern.edu/individual/n_vcard_'
org_prefix     = 'http://vivo.northwestern.edu/individual/n_org_'

# Setup logging
logging.basicConfig()


def parse_name(name):
    name_dict = dict()
    if len(name) > 0:
        name_parts = name.split(' ')
        if len(name_parts) == 1:
            name_dict['family_name'] = name_parts[0]
            name_dict['given_name'] = ''
            name_dict['additional_name'] = ''
        elif len(name_parts) == 2:
            name_dict['given_name'] = name_parts[0]
            name_dict['additional_name'] = ''
            name_dict['family_name'] = name_parts[1]
        elif len(name_parts) == 3:
            name_dict['given_name'] = name_parts[0]
            name_dict['additional_name'] = name_parts[1]
            name_dict['family_name'] = name_parts[2]
        else:
            name_dict['given_name'] = name_parts[0]
            name_dict['additional_name'] = name_parts[1]
            name_dict['family_name'] = name_parts[2:]
    return name_dict


def graph_dataset(dataset_data):
    """
    Given jkan data from json file, make a dcat dataset

    :param dataset_data: a dict containing the dataset's data
    :return: triples added to graph
    """
    graph = Graph()
    dataset_uri = URIRef(dataset_prefix + dataset_data['basename'])
    graph.add((dataset_uri, RDF.type, DCAT.Dataset))
    # add both rdfs:label and dcterms:title to match dcat ontology and for value to show in vivo
    graph.add((dataset_uri, RDFS.label, Literal(dataset_data['title'].strip())))
    graph.add((dataset_uri, DCTERMS.title, Literal(dataset_data['title'].strip())))
    # add both vivo:description and dcterms:description to match dcat ontology and for value to show in vivo
    graph.add((dataset_uri, VIVO.description, Literal(dataset_data['notes'].strip())))
    graph.add((dataset_uri, DCTERMS.description, Literal(dataset_data['notes'].strip())))
    for kw in dataset_data['category']:
        graph.add((dataset_uri, DCAT.keyword, Literal(kw)))

    if 'resources' in dataset_data:
        for resource in dataset_data['resources']:
            if len(resource['name']) > 0:
                resource_uri = dataset_uri + '-' + resource['name'].replace (" ", "_").replace("(", "").replace(")", "").lower()
                graph.add((resource_uri, RDF.type, DCAT.Distribution))
                graph.add((resource_uri, RDFS.label, Literal(resource['name'])))
                if len(resource['format']) > 0:
                    if resource['format'] == 'html':
                        graph.add((resource_uri, DCAT.mediaType, Literal('text/html')))
                    elif resource['format'] == 'json':
                        graph.add((resource_uri, DCAT.mediaType, Literal('application/json')))
                if len(resource['url']) > 0:
                    graph.add((resource_uri, DCAT.accessURL, Literal(resource['url'])))

                graph.add((dataset_uri, DCAT.distribution, resource_uri))
                
    graph = graph_maintainer(graph, dataset_data, dataset_uri)

    if len(dataset_data['organization']) > 0:
        org_uri = URIRef(org_prefix + dataset_data['organization'].replace (" ", "_").lower())
        graph.add((org_uri, RDF.type, FOAF.Organization))
        graph.add((dataset_uri, DCTERMS.publisher, org_uri))

    return graph

def graph_maintainer(graph, dataset_data, dataset_uri):
    if len(dataset_data['maintainer']) > 0 or len(dataset_data['maintainer_email']) > 0:
        """
        Make a vcard name and or email out for the maintainer
        """
        vcard_uri = URIRef(vcard_prefix + dataset_data['basename'] + '-vcard')
        graph.add((vcard_uri, RDF.type, VCARD.Kind))
        # label for vcard/ns#Kind
        if len(dataset_data['maintainer']) > 0:
            graph.add((vcard_uri, RDFS.label, Literal(dataset_data['maintainer'] + ' VCard')))
        else:
            graph.add((vcard_uri, RDFS.label, Literal(dataset_data['maintainer_email'] + ' VCard')))
        # then deal with vcard/ns#Name
        if len(dataset_data['maintainer']) > 0:
            name_uri = URIRef(str(vcard_uri) + '-name')
            graph.add((vcard_uri, VCARD.hasName, name_uri))
            graph.add((name_uri, RDF.type, VCARD.Name))
            name_dict = parse_name(dataset_data['maintainer'])
            if len(name_dict['given_name']) > 0:
                graph.add((name_uri, VCARD.givenName, Literal(name_dict['given_name'])))
            if len(name_dict['family_name']) > 0:
                graph.add((name_uri, VCARD.familyName, Literal(name_dict['family_name'])))
            if len(name_dict['additional_name']) > 0:
                graph.add((name_uri, VCARD.additionalName, Literal(name_dict['additional_name'])))
        # and vcard/ns#Email
        if len(dataset_data['maintainer_email']) > 0:
            email_uri = URIRef(str(vcard_uri) + '-email')
            graph.add((vcard_uri, VCARD.hasEmail, email_uri))
            graph.add((email_uri, RDF.type, VCARD.Email))
            graph.add((email_uri, VCARD.email, Literal(dataset_data['maintainer_email'])))
        # then add vcard to dataset
        graph.add((dataset_uri, DCAT.contactPoint, vcard_uri))
    return graph

# Main
if __name__ == '__main__':
    dataset_graph = Graph()
    dataset_dir = os.path.dirname(os.path.realpath(__file__)) + '/datasets/'
    for filename in os.listdir(dataset_dir):
        with open(dataset_dir + filename) as data_file:
            dataset_data = json.load(data_file)
            dataset_graph += graph_dataset(dataset_data)

            triples_file = open('public/datasets.rdf', 'w')
            print(dataset_graph.serialize(format='pretty-xml').decode('utf-8'), sep="", end="", file=triples_file)
            # triples_file = open('public/datasets.ttl', 'w')
            # print(dataset_graph.serialize(format='turtle').decode('utf-8'), sep="", end="", file=triples_file)
            triples_file.close()