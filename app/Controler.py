'''
Created on Sep 11, 2014

@author: Clint Liddick
'''

import webapp2 
import logging
from string import Template
from time import strftime

# logging setup
# TODO set to INFO in production
logging.getLogger(__name__).setLevel(logging.DEBUG)

# Handler classes
class IntroHandler(webapp2.RequestHandler):
    """RequestHandler for initial intro page"""
    
    def get(self):
        """Intro page GET request handler"""
        logging.debug('GET request: ' + str(self.request))

        # create raw html string for template
        htmlstr = self.buildIntroHTMLString()
        
        # create template
        htmltmpl = Template(htmlstr)
        
        # map dynamic content elements
        mapping = self.buildIntroMapping()
        
        # substitute mapped tags
        htmlout = htmltmpl.substitute(mapping)
        
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(htmlout)
        
        
    def buildIntroHTMLString(self):
        htmlstr = ''
        with open('html/head.tmpl', 'r') as headfile:
            htmlstr += headfile.read()
        
        with open('html/header.tmpl', 'r') as headerfile:
            htmlstr += headerfile.read()
            
        with open('html/body.tmpl', 'r') as bodyfile:
            htmlstr += bodyfile.read()
            
        with open('html/footer.tmpl', 'r') as footerfile:
            htmlstr += footerfile.read()
            
        return htmlstr
    
    
    def buildIntroMapping(self):
        """ Determine and return template tag mapping """
        mapping = dict()
        mapping['page_title'] = 'Pitt Chalkboard'
        mapping['current_year'] = strftime('%Y')
        return mapping
    
    
    def handle_exception(self, exception, debug):
        # overrides the built-in master exception hanlder
        logging.error('Template mapping exception, unmapped tag: ' + str(exception))
        return self.redirect(uri='/error', code=307) # TODO create general error page


# list of URI/Handler routing tuples
# the URI is a regular expression beginning with root '/' char
routeHandlers=[
        (r'/',IntroHandler),
]

# application object 
application = webapp2.WSGIApplication(routeHandlers,debug=True)