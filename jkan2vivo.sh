#!/bin/bash
cd ~/work/jkan
git pull

cd ~/work/markdown-to-json
sh ./jkan2json.sh

cd ~/work/jkan2rdf
python ./datasets-rdf.py 

curl -d "email=$VIVO_ROOT_USER" -d "password=$VIVO_ROOT_PASSWORD" -d '@import.sparql' 'http://localhost:8080/vivo/api/sparqlUpdate'