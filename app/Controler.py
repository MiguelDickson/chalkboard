'''
Created on Sep 11, 2014

@author: Clint Liddick
'''

import webapp2 
import logging

# logging setup
# TODO set to INFO in production
logging.getLogger(__name__).setLevel(logging.DEBUG)

# Handler classes
class IntroHandler(webapp2.RequestHandler):
    """RequestHandler for initial intro page"""
    
    tempHtml = '<html><head><title>test</title></head><body><h2>Hello!</h2></body></html>'
    # TODO parse template files
    
    def get(self):
        """GET request handler"""
        logging.debug('GET request: ' + str(self.request))
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(self.tempHtml)



# list of URI/Handler tuples
routeHandlers=[
        (r'/',IntroHandler),
]

# application object 
application = webapp2.WSGIApplication(routeHandlers,debug=True)