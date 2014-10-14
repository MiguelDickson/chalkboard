import os
import webapp2
import logging
from google.appengine.ext.webapp import template
from google.appengine.api import users 			
from google.appengine.ext import db 			 
from datetime import date

# logging setup
# TODO set to INFO in production
logging.getLogger(__name__).setLevel(logging.DEBUG)


# General Utilities
def renderTemplate(response, templatename, templatevalues) :
    basepath = os.path.split(os.path.dirname(__file__)) #extract the base path, since we are in the "app" folder instead of the root folder
    path = os.path.join(basepath[0], 'templates/' + templatename)
    html = template.render(path, templatevalues)
	
    response.out.write(html)

def handle404(request, response, exception) :
    """ Custom 404 error page """
    logging.debug('404 Error GET request: ' + str(request))
    logging.exception(exception)
    
    template_values = {
        'page_title' : "Page Not Found",
        'current_year' : date.today().year
    }
		
    renderTemplate(response, '404.html', template_values)


# Handler classes
class IntroHandler(webapp2.RequestHandler):
    """RequestHandler for initial intro page"""

    def get(self):
        """Intro page GET request handler"""
        logging.debug('IntroHandler GET request: ' + str(self.request))
		
        template_values = {
            'page_title' : "Chalkboard",
            'current_year' : date.today().year
        }
		
        renderTemplate(self.response, 'index.html', template_values)
		
    def handle_exception(self, exception, debug):
        # overrides the built-in master exception handler
        logging.error('Template mapping exception, unmapped tag: ' + str(exception))
        
        return self.redirect(uri='/error', code=307)

class InstructorHandler(webapp2.RequestHandler):
    """RequestHandler for instructor page"""

    def get(self):
        """Instructor page GET request handler"""
        logging.debug('InstructorHandler GET request: ' + str(self.request))
		
        template_values = {
            'page_title' : "Chalkboard",
            'current_year' : date.today().year
        }
		
        renderTemplate(self.response, 'instructor.html', template_values)
		
    def handle_exception(self, exception, debug):
        # overrides the built-in master exception handler
        logging.error('Template mapping exception, unmapped tag: ' + str(exception))
        
        return self.redirect(uri='/error', code=307)

class ErrorHandler(webapp2.RequestHandler):
    """Request handler for error pages"""

    def get(self):
        logging.debug('ErrorHandler GET request: ' + str(self.request))

        template_values = {
            'page_title' : "Oh no...",
            'current_year' : date.today().year
        }
		
        renderTemplate(self.response, 'error.html', template_values)

class AboutHandler(webapp2.RequestHandler) :
    """Request handler for about page"""

    def get(self):
        logging.debug('AboutHandler GET request: ' + str(self.request))

        template_values = {
            'page_title' : "About Chalkboard",
            'current_year' : date.today().year
        }

        renderTemplate(self.response, 'about.html', template_values)


# list of URI/Handler routing tuples
# the URI is a regular expression beginning with root '/' char
routeHandlers = [
    (r'/', IntroHandler),
	(r'/about', AboutHandler),
    (r'/error', ErrorHandler),
    (r'/instructor', InstructorHandler)
]

# application object
application = webapp2.WSGIApplication(routeHandlers, debug=True)

application.error_handlers[404] = handle404
