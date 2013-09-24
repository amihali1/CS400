#!/usr/bin/env python
from google.appengine.ext import ndb,blobstore
from google.appengine.api import users,memcache,search,files
from datetime import datetime
from functions import *
import logging
import json
#-------------------------------
# MODELS
#-------------------------------
#class Store(ndb.Model):
#    store_id = ndb.IntegerProperty(required=True)
#    store_name = ndb.StringProperty(required=True)
#    store_location = ndb.GeoPtProperty()
#    
#    @staticmethod
#    def get(store_id):
#        if store_id:
#            try:
#                store = Store.query().filter(Store.store_id == store_id).get()
#                if not store:
#                    return None
#                return store
#            except:
#                return None
#        return None   
#    
#    
#class Item(ndb.Model):
#    item_id = ndb.IntegerProperty(required=True)
#    item_name = ndb.StringProperty()
#    item_desc = ndb.TextProperty()
#    item_price = ndb.FloatProperty(required=True)
#    item_store_number = ndb.KeyProperty(required=True)
#    item_rating = ndb.KeyProperty()
#    item_in_stock = ndb.BooleanProperty(default=False, required=True)
#    
#    @staticmethod
#    def get(item_id):
#        if item_id:
#            try:
#                item = Item.query().filter(Item.item_id == item_id).get()
#                if not item:
#                    return None
#                return item
#            except:
#                return None
#        return None
#    
class Query(ndb.Model):
    query_value = ndb.StringProperty(required=True)
    #def save(self):
    #    self.put()
    #    
    #def get(self):
    #    results = search.Index(name='queries').search(self.query_value)
    #    if not results:
    #        try:
    #            search.Index(name='queries').put(createQueryDocument(self))
    #            results = search.Index(name='queries').search(self.query_value)
    #        except:
    #            logging.error('Could not create index for query')        
    #    return results