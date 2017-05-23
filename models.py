import webapp2
import re
import cgi
import jinja2
import os
from google.appengine.api import users

import session_module
from webapp2_extras import sessions 


from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Visitante(ndb.Model):
	nombre=ndb.StringProperty()
	email=ndb.StringProperty()
	password=ndb.StringProperty(indexed=True)
	creado=ndb.DateTimeProperty(auto_now_add=True)

class Question(ndb.Model):
	question=ndb.StringProperty()
	first=ndb.StringProperty()
	second=ndb.StringProperty()
	third=ndb.StringProperty()
	theme=ndb.StringProperty()
	correct=ndb.StringProperty()
	creado=ndb.DateTimeProperty(auto_now_add=True)