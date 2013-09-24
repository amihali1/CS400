#!/usr/bin/env python
import webapp2
from views import *
        
app = webapp2.WSGIApplication([
    ('/', HomePage),
    ], debug=True)

def main():
    run_wsgi_app(app)
    
if __name__ == '__main__':
    main()


