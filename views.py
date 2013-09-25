#!/usr/bin/env python
import webapp2
import os
import re
import logging
import jinja2
import urllib
from google.appengine.api import users,search,memcache,mail,urlfetch,images
from google.appengine.ext import db,blobstore
from google.appengine.ext.webapp import blobstore_handlers
from models import *

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#--------------------
# Request Handlers
#--------------------
class HomePage(webapp2.RequestHandler):
    def get(self):
        try:
            query = self.request.GET["term"]
        except:
            query = None
        template_values = {}
        if query:
            template_values = {'results':1,'q':query}
        template = jinja_environment.get_template('/templates/index.html')
        self.response.out.write(template.render(template_values))
    
#class Login(webapp2.RequestHandler):
#    def get(self):
#        user = users.get_current_user()
#        if not user:
#            login_url = users.create_login_url(self.request.referer)
#            self.redirect(login_url)
#        else:
#            self.redirect(self.request.path)
#
#class Logout(webapp2.RequestHandler):
#    def get(self):
#        user = users.get_current_user()
#        if not user:
#            #if user wasnt logged in to begin with, just redirect them to home page 
#            self.redirect('/')
#        else:
#            #remove user from memcache and logout
#            memcache.delete('%s:profile' % user.user_id())
#            self.redirect(users.create_logout_url('/'))
#
#class ImageHandler(blobstore_handlers.BlobstoreDownloadHandler):
#    def get(self):
#        key = self.request.get('key')
#        #blob_info = blobstore.BlobInfo.get(key)
#        try:
#            image_url = images.get_serving_url(key)
#            image = urlfetch.fetch(image_url)
#            self.response.headers['Content-Type'] = "image/jpg"
#            self.response.out.write(image.content)
#        except:
#            image_url = images.get_serving_url('RLbZ9HLtpo0hDIhxDLlM3D0WJcMIcaSmg07eWWLOkXHn8HZnTN4MJbIjiPYytioi')
#            image = urlfetch.fetch(image_url)
#            self.response.headers['Content-Type'] = "image/jpg"
#            self.response.out.write(image.content)
#
#
#class ErrorHandler(webapp2.RequestHandler):
#    def get(self):
#        user = users.get_current_user()
#        template_values = {'user':user}
#        template = jinja_environment.get_template('/templates/error.html')
#        self.response.out.write(template.render(template_values))

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        walmart_api_key = 'nkb83uzran3m7vhp7bvjeejt'
        best_buy_api_key = '5tkbrm84yzcfu2e64axsp7ux'
        query = self.request.GET["term"]
        q = Query(query_value=query)
        #save is a UDF in the model that we use instead of put()
        #so that we can do some extra processing on it
        expr_list = [search.SortExpression(
            expression='query', default_value='',
            direction=search.SortExpression.ASCENDING)]
        
        # construct the sort options
        sort_opts = search.SortOptions(expressions=expr_list,limit=7)
        query_options = search.QueryOptions(limit=7,sort_options=sort_opts,returned_fields=['value'])
        query_obj = search.Query(query_string=q.query_value, options=query_options)
        results = search.Index(name='queries').search(query=query_obj)
        try:
            ajax = self.request.GET['ajax']
        except:
            ajax = 0

        #if the number of results is 0 and we are not searching via ajax, then create new document for the query
        if results.number_found == 0 and ajax == 0:
            try:
                search.Index(name="queries").put(create_query_document(q))
                results = search.Index(name="queries").search(query=q.query_value)
            except:
                logging.exception('Could not create search document for query: ' + q.query_value)
                
        if ajax:
            queries = []
            for r in results:
                objs = {'q':r.fields[0].value}
                queries.append(objs)
            self.response.out.write(json.dumps(queries))
        else:
            total_results = 0
            items = {}
            #encode query b/c apis may not accept multiple word queries. So replace spaces between words with a +
            encoded_query = query.replace(' ','+')
            
            #for best buy, we want to add wildcard * in order to search for items not identical to query
            #but where query is just included somewhere in name or desc
            temp = query.split(' ')
            if len(temp) == 1:
                best_buy_encoded_query = query + '*'
            else:
                temp[-1] = temp[-1] + '*'
                temp = '*|name='.join(temp)
                best_buy_encoded_query = temp

            #parse the JSON that we get back from API calls so that we can access each of the parts via code
            walmart_results = json.loads(urlfetch.fetch("http://api.walmartlabs.com/v1/search?apiKey="+walmart_api_key+"&query="+encoded_query+"&categoryId=3944&sort=relevance&ord=asc").content)
            best_buy_results = json.loads(urlfetch.fetch("http://api.remix.bestbuy.com/v1/products(name="+best_buy_encoded_query+")?format=json&show=name,regularPrice,onlineAvailability,thumbnailImage,url&apiKey="+best_buy_api_key).content)
            #self.response.out.write(best_buy_results)
            #return
            #make sure we have items to show
            try:
                walmart_items = []
                #make sure they have it in stock since thats the whole point of this project
                for item in walmart_results['items']:
                    if item['availableOnline']:
                        walmart_items.append(item)
            except:
                walmart_items = []
            try:
                best_buy_items = []
                for item in best_buy_results['products']:
                    if item['onlineAvailability']:
                        best_buy_items.append(item)
            except:
                best_buy_items = []
                
            items['walmart'] = walmart_items
            items['best_buy'] = best_buy_items
            total_results += int(walmart_results['totalResults']) + int(best_buy_results['total'])
            template_values = {'results':results,'q':q.query_value,'number_results':total_results,'items':items}
            template = jinja_environment.get_template('/templates/index.html')
            self.response.out.write(template.render(template_values))#walmart_results)#
        
app = webapp2.WSGIApplication([
('/$', HomePage),
#('/login[/]?$',Login),
#('/logout[/]?$',Logout),
#('/get-image',ImageHandler),
#('/error[/]?$',ErrorHandler),
('/search[/]?$', SearchHandler),
#('/.*',ErrorHandler)
], debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == '__main__':
    main()
