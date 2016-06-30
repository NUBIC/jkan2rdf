#!/bin/bash
rm -rf datasets/*

cp ~/work/rdcat/output/datasets/*.json ./datasets/

python ./datasets-rdf.py 

curl -d "email=$VIVO_ROOT_USER" -d "password=$VIVO_ROOT_PASSWORD" -d '@import.sparql' 'http://localhost:8080/vivo/api/sparqlUpdate'