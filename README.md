# jkan2rdf

[jkan](https://github.com/timwis/jkan) is a lightweight, backend-free open data portal, powered by Jekyll.

This project takes the datasets created by jkan and will transform those datasets into RDF triples adhering to the [dcat](https://www.w3.org/TR/vocab-dcat/) ontology.  Ultimately, this data can be loaded into [VIVO](http://vivoweb.org/).

First, the we get the latest data from jkan. 

Then, the jkan markdown data is transformed into json using the [markdown-to-json](https://github.com/scottstanfield/markdown-to-json) node.js project. 

The datasets-rdf.py script will read the json data and transform it into rdf, outputting that data into the public directory.  Using [pow](http://pow.cx/) the rdf can be served as a [static file](http://pow.cx/manual.html#section_2.4) for use as an IRIref in the SPARQL [load](https://www.w3.org/Submission/SPARQL-Update/#rLoad) operation. 

Finally, using the [VIVO Sparql Update API](https://wiki.duraspace.org/display/VIVO/The+SPARQL+Update+API), the data is loaded into VIVO. 
