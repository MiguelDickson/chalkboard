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


# General Utilities

def buildHeading():
    """returns the <head> and header HTML"""
    htmlstr = ''
    with open('html/head.tmpl', 'r') as headfile:
        htmlstr += headfile.read()

    with open('html/header.tmpl', 'r') as headerfile:
        htmlstr += headerfile.read()

    return htmlstr


def buildFooter():
    """returns the footer and HTML closing"""
    htmlstr = ''
    with open('html/footer.tmpl', 'r') as footerfile:
        htmlstr = footerfile.read()

    return htmlstr


def buildBaseMapping():
    """ Determine and return template tag mapping """
    mapping = dict()
    mapping['page_title'] = 'Pitt Chalkboard'
    mapping['current_year'] = strftime('%Y')
    return mapping

def handle404(request, response, exception):
    """ Custom 404 error page """
    
    logging.exception(exception)
    htmlstr = buildHeading()
    with open('html/404.tmpl', 'r') as errorfile:
        htmlstr += errorfile.read()
        htmlstr += buildFooter()

    htmltmpl = Template(htmlstr)
    mapping = buildBaseMapping()
    htmlout = htmltmpl.substitute(mapping)

    response.headers['Content-Type'] = 'text/html'
    response.set_status(404)
    response.write(htmlout)


# Handler classes
class IntroHandler(webapp2.RequestHandler):

    """RequestHandler for initial intro page"""

    def get(self):
        """Intro page GET request handler"""
        logging.debug('GET request: ' + str(self.request))

        # create raw html string for template
        htmlstr = buildHeading()
        htmlstr += self.buildIntroHTMLString()
        htmlstr += buildFooter()

        # create template
        htmltmpl = Template(htmlstr)

        # map dynamic content elements
        mapping = buildBaseMapping()

        # substitute mapped tags
        htmlout = htmltmpl.substitute(mapping)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(htmlout)

    def buildIntroHTMLString(self):
        htmlstr = ''
        with open('html/introbody.tmpl', 'r') as bodyfile:
            htmlstr += bodyfile.read()

        return htmlstr

    def handle_exception(self, exception, debug):
        # overrides the built-in master exception handler
        logging.error(
            'Template mapping exception, unmapped tag: ' + str(exception))
        # TODO create general error page
        return self.redirect(uri='/error', code=307)


class ErrorHandler(webapp2.RequestHandler):

    """Request handler for error pages"""

    def get(self):
        logging.debug('GET request: ' + str(self.request))

        htmlstr = buildHeading()
        with open('html/error.tmpl', 'r') as errorfile:
            htmlstr += errorfile.read()
        htmlstr += buildFooter()
        
        htmltmpl = Template(htmlstr)
        mapping = buildBaseMapping()
        htmlout = htmltmpl.substitute(mapping)
        
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(htmlout)



# list of URI/Handler routing tuples
# the URI is a regular expression beginning with root '/' char
routeHandlers = [
    (r'/', IntroHandler),
    (r'/error', ErrorHandler),
]

# application object
application = webapp2.WSGIApplication(routeHandlers, debug=True)

application.error_handlers[404] = handle404
