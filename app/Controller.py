import os
import webapp2
import logging
from google.appengine.ext.webapp import template
from google.appengine.api import users         
from google.appengine.api import mail    
from google.appengine.ext import db 
from google.appengine.ext import blobstore     
from google.appengine.ext.webapp import blobstore_handlers         
from datetime import date

# logging setup
# TODO set to INFO in production
logging.getLogger(__name__).setLevel(logging.DEBUG)


# General Utilities
class CourseData(db.Model):
    document_list = db.ListProperty(blobstore.BlobKey,indexed=False, default=[]) #Stores the keys for a list of documents
    course_name = db.StringProperty()
    course_number = db.IntegerProperty()
    student_list = db.StringListProperty() #Stores a list of string (emails)
    course_id = db.StringProperty() #unique course ID
    department = db.StringProperty()
    university = db.StringProperty()
    instructor = db.StringProperty()
    email = db.StringProperty()
    year = db.IntegerProperty()
    semester = db.StringProperty()
    syllabus = blobstore.BlobReferenceProperty() #Store the reference to syllabus in blobstore
    is_active = db.BooleanProperty()
    #TODO: calendar entry goes here eventually (not sure how to store it since this task should be hard)

class UserData(db.Model) :
    user_id = db.StringProperty()
    user_name = db.StringProperty()
    user_email = db.StringProperty()
    courses = db.ListProperty(db.Key) #Stores a list of keys for courses
    is_active = db.BooleanProperty()
    current_course_selected = db.StringProperty()


def generateURL() :
    return "/course/123" #TODO: Generate real IDs
    
def generateClassEmails(student_list) : 
    class_list = ""
    l = len(student_list)
    #logging.error("The length of the student list is:")
    #logging.error(l)
    for num in xrange(0, l-2):
        class_list += student_list[num]
        class_list += ","
    class_list+=student_list[len(student_list)-1]
    return class_list
        

def generateID() :
    return '1234' #TODO: Generate real IDs


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
        
class NewCourseHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url('/')
            template_values = {
                'page_title' : "Chalkboard",
                'current_year' : date.today().year,
                'logout' : logout_url,
            
            }
        
        renderTemplate(self.response, 'new_course.html', template_values)
        
class InstructorHandler(webapp2.RequestHandler):
    """RequestHandler for instructor page"""   
    def post(self):
        logging.debug('Instructorandler POST request: ' + str(self.request))
        
        #retrieve the current user
        user = users.get_current_user()
        
        login_url = ''
        logout_url = '';
        
        target_page = 'instructor.html'
        
        template_values = {
            
        }
        
        if user :
            #grab all the post parameters and store into a course db model
            course = CourseData()
            
            course.course_name = self.request.get('course')
            course.instructor = self.request.get('name')
            course.email = self.request.get('email')
            course.course_number = int(self.request.get('number'))
            course.university = self.request.get('university')
            course.department = self.request.get('department')
            course.semester = self.request.get('semester')
            course.year = int(self.request.get('year'))
            course.student_list = ['mlucient@gmail.com']
            course.is_active = True
            course.course_id = generateID()
            course.documents_list = [""]
            course.syllabus = None
            
            course.put()
            
            
            d = UserData.all()
            d.filter('user_id =', user.user_id())
            
            if d.count(0) :
                #stores data since no user with this ID is found
                user_data = UserData()
                user_data.user_id = user.user_id()
                user_data.user_name = user.nickname()            
                user_data.user_email = user.email()    
                user_data.is_active = True
                user_data.courses = [course]
                user_data.current_course_selected = course.course_id
                
                user_data.put()
            else :
                for user_data in d.run():
                    user_data.current_course_selected = course.course_id
                    user_data.courses.append(course.key()) #Add course key to user data
                    user_data.put()
            
            template_values = {
                'page_title' : "Chalkboard",
                'current_year' : date.today().year,
                'logout' : users.create_logout_url('/'),
                'courses' : CourseData.get(user_data.courses)
            }
        else : 
            self.redirect(users.create_login_url('/instructor'))   
            
        renderTemplate(self.response, target_page, template_values)
    
    def get(self):
        """Instructor page GET request handler"""
        logging.debug('InstructorHandler GET request: ' + str(self.request))
    
        #retrieve the current user
        user = users.get_current_user()
        
        login_url = ''
        logout_url = ''
        
        email = ''
        name = ''
        course = ''
                
        template_values = {
        
        }
        
        #check if signed in
        if user:
            logout_url = users.create_logout_url('/')
                        
            d = UserData.all()
            d.filter('user_id =', user.user_id())
            
            #if data was received, grab it
            if d.count(1):
                for user_data in d.run():
                
					#If we have at least a course, display them
							
                    template_values = {
                        'page_title' : "Chalkboard",
                        'current_year' : date.today().year,
                        'logout' : logout_url,
                        'courses' : CourseData.get(user_data.courses)
                    }
            #if no data was received, add data entry
            else:
                #stores data
                user_data = UserData()
            
                user_data.user_id = user.user_id()
                user_data.user_name = user.nickname()            
                user_data.user_email = user.email()    
                user_data.is_active = True
                user_data.courses = []
            
                user_data.put()
            
                logout_url = users.create_logout_url('/')
            
                template_values = {
                    'page_title' : "Chalkboard",
                    'current_year' : date.today().year,
                    'logout' : logout_url,
                    'courses' : CourseData.get(user_data.courses)
                }
                
        else :
            self.redirect(users.create_login_url('/instructor'))        
        
        
        renderTemplate(self.response, 'instructor.html', template_values)

    def handle_exception(self, exception, debug):
        # overrides the built-in master exception handler
        logging.error('Template mapping exception, unmapped tag: ' + str(exception))
        
        return self.redirect(uri='/error', code=307)

class DocumentsHandler(webapp2.RequestHandler):
    #"""RequestHandler for Documents page"""
    def post(self):
        
        name = self.request.get('name')
        email = self.request.get('email')
        course = self.request.get('course')
        
        logging.debug('DocumentsHandler POST request: ' + str(self.request))
    
        user = users.get_current_user();
        
        template_values = {}
        if user:
            #stores data
                        
            logout_url = users.create_logout_url('/')
            
            template_values = {
                'page_title' : "Chalkboard",
                'current_year' : date.today().year,
                'logout' : logout_url,
                'courses' : CourseData.get(user_data.courses)
            }
            
        else:
            self.redirect(users.create_login_url('/instructor'))

        #redirects back to instructor page (should show new data)
        #renderTemplate(self.response, 'instructor.html', template_values)
    
    def get(self):
        upload_url = blobstore.create_upload_url('/upload');
    
        """Instructor page GET request handler"""
        logging.debug('UploadHandler GET request: ' + str(self.request))
    
        #retrieve the current user
        user = users.get_current_user()
    
        target_page = 'documents.html'
                
        #check if signed in
        if user:
            logout_url = users.create_logout_url('/')
                        
            d = UserData.all()
            d.filter('user_id =', user.user_id())
            
            #if data was received, grab it
            if d.count(1):
                for user_data in d.run():
                    email = user_data.user_email
                    name = user_data.user_name
                    course = user_data.course_name
                
                template_values = {
                    'page_title' : "Chalkboard",
                    'current_year' : date.today().year,
                    'logout' : logout_url,
                    'courses' : CourseData.get(user_data.courses),
                    'upload_url' : upload_url
                }
            #if no data was received, redirect to new course page (to make data)
            else:
                target_page = 'instructor.html'
                            
        else :
            self.redirect(users.create_login_url('/instructor'))        
        
        
        renderTemplate(self.response, target_page, template_values)

    def handle_exception(self, exception, debug):
        # overrides the built-in master exception handler
        logging.error('Template mapping exception, unmapped tag: ' + str(exception))
        
        return self.redirect(uri='/error', code=307)

class SendEmailHandler(webapp2.RequestHandler):
    def get(self):
        #logging.error('Here succesfully, I guess...')
        user = users.get_current_user()
        if user is None:
            #logging.error('SendEmail Handler: not logged in for some reason.')    
        if user:
            logout_url = users.create_logout_url('/')
            d = UserData.all()
            d.filter('user_id =', user.user_id())
            if d.count(1):
                #logging.error('Here all right so far. #2')
                for user_data in d.run():
                    current_course = user_data.current_course_selected
                    logging.error(current_course)
                    e = CourseData.all()
                    e.filter('course_id =', current_course)
                    if e.count(1):
                        #logging.error('Here all right so far. #3')
                        for course_info in e.run():
                            students = course_info.student_list     
                            template_values = {
                                'current_course' : course_info,
                                'student_list' : students,
                                'page_title' : "Chalkboard",
                                'current_year' : date.today().year,
                                'logout' : users.get_logout_url     
                                'login' : users.get_login_url  
                                'user' : users.get_current_user
                            }
                        renderTemplate(self.response, 'send_email.html', template_values)                            
                    else:
                        self.redirect('/instructor'))
            else:
                self.redirect('/insructor')           
        else:
            self.redirect('/instructor'))
        
        
 
class EmailHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user is None:
            self.redirect('/instructor')
        message = mail.EmailMessage()
        message.sender = user.email()
        d = UserData.all()
        d.filter('user_id =', user.user_id())
        for user_data in d.run(): 
            current_course = user_data.current_course_selected
            #logging.error(current_course)
            e = CourseData.all()
            e.filter('course_id =', current_course)
            for course_info in e.run():
                stu_list = course_info.student_list
                bcc_list = generateClassEmails(stu_list)
                #logging.error("The first student in the list is: " + stu_list[0])
                #logging.error("The message body was:" + self.request.get('message_body'))
                message.bcc = bcc_list
                message.body = self.request.get('message_body')
                message.to = user.email()
                message.send()
                self.redirect(users.create_
        
        
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler) :
    def post(self):
        logging.debug('UploadHandler POST request: ' + str(self.request))
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0];
        self.redirect('/instructor')
        user = users.get_current_user();
        d = UserData.all()
        d.filter('user_id =', user.user_id())
        if d.count(1):
            for user_data in d.run():
                user_data.documentlist.append(blob_info.key());
                user_data.put();
        
        
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
        
class CourseHandler(webapp2.RequestHandler) :
    """Request handler for Course pages (public view)"""
    def get(self, id):
        logging.debug('CourseHandler GET request: ' + str(self.request) + id)
        
        user = users.get_current_user()
        
        login_url = ''
        logout_url = ''
        
        if(user):
            logout_url = users.create_logout_url('/')
        else:
            login_url = users.create_login_url('/')
            
        d = CourseData.all()
        d.filter('course_id =', id)
            
        if d.count(1):
            for course in d.run():
                template_values = {
                    'page_title' : "Chalkboard",
                    'current_year' : date.today().year,
                    'logout' : logout_url,
                    'login' : login_url,
                    'course_name' : course.course_name,
                    'course_number' : course.course_number,
                    'student_list' : course.student_list,
                    'department' : course.department,
                    'university' : course.university,
                    'instructor' : course.instructor,
                    'email' : course.email,
                    'year' : course.year,
                    'semester' : course.semester,
                    'is_active' : course.is_active,
                    'course_id' : course.course_id
                }
            print "JHIDS"    
            renderTemplate(self.response, 'course.html', template_values) 
        else:
        #redirect to error if course wasn't found (or if 2 courses share an ID???)
            renderTemplate(self.response, 'error.html', template_values)

# list of URI/Handler routing tuples
# the URI is a regular expression beginning with root '/' char
routeHandlers = [
    (r'/', IntroHandler),
    (r'/about', AboutHandler),
    (r'/error', ErrorHandler),
    (r'/instructor', InstructorHandler),
    (r'/new_course', NewCourseHandler),
    (r'/documents', DocumentsHandler),
    (r'/upload', UploadHandler),
    (r'/send_email', SendEmailHandler),
    (r'/email', EmailHandler),
    (r'/course/.*', CourseHandler), #Default catch all to handle a course page request
    (r'/course/(\d+)', CourseHandler), #Default catch all to handle a course page request
    (r'/.*', ErrorHandler)
]

# application object
application = webapp2.WSGIApplication(routeHandlers, debug=True)

application.error_handlers[404] = handle404
