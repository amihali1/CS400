#!/usr/bin/env python
import jinja2
import logging
import os
import webapp2
from google.appengine.api import search,users,files
from google.appengine.ext import blobstore

def build_suggestions(str):
    suggestions = []
    for word in str.split():
        prefix = ""
        for letter in word:
            prefix += letter
            suggestions.append(prefix)
    return ' '.join(suggestions)

def create_query_document(query):
	if query:
		try:
			return search.Document(doc_id=query.key, fields=[search.TextField(name='query', value=build_suggestions(query.query_value)),
															 search.TextField(name='value', value=query.query_value),])
		except search.Error:
			logging.exception('Couldnt create index blah')
	else:
		return
	
def xml_to_json(xml_string):
	return