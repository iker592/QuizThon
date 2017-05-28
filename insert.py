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

from models import *

class InsertHandler(session_module.BaseSessionHandler):

	def write_form (self, question="", firstopt="", secondopt="",thirdopt="", question_error="", firstopt_error="",	secondopt_error="", thirdopt_error="",correct="",correct_error="",theme="",theme_error=""):
		tem_values= {"question" :
		question,"firstopt" : firstopt,
		"secondopt" : secondopt,
		"thirdopt" : thirdopt,
		"question_error" : question_error,
		"firstopt_error" : firstopt_error,
		"secondopt_error" : secondopt_error,
		"thirdopt_error" : thirdopt_error,
		"correct" : correct,
		"correct_error" : correct_error,
		"theme" : theme,
		"theme_error" : theme_error}
		template = JINJA_ENVIRONMENT.get_template('insert.html')
		self.response.write(template.render(tem_values))

	def get(self):
		self.write_form()

	def post(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		QUESTION_RE = re.compile(r"^[a-zA-Z0-9_-]+( [a-zA-Z0-9_?]+)*$")
		def valid_question(question):
			return QUESTION_RE.match(question)
		u_question = self.request.get('question')
		u_firstopt = self.request.get('firstopt')
		u_secondopt = self.request.get('secondopt')
		u_thirdopt = self.request.get('thirdopt')
		u_theme = self.request.get('theme')
		u_correct = self.request.get('correct')

		sani_question = escape_html(u_question)
		sani_firstopt = escape_html(u_firstopt)
		sani_secondopt = escape_html(u_secondopt)
		sani_thirdopt = escape_html(u_thirdopt)
		sani_theme = escape_html(u_theme)
		sani_correct = escape_html(u_correct)
		question_error = ""
		firstopt_error = ""
		secondopt_error = "" 
		thirdopt_error = ""
		correct_error = ""
		theme_error = ""
		question=""
		error = False
		if not valid_question(u_question):
			question_error = "Wrong type question!"
			error = True
		if not valid_question(u_firstopt):
			firstopt_error = "Wrong type of answer in first option!"
			error = True
		if not valid_question(u_secondopt):
			secondopt_error = "Wrong type of answer in second option!"
			error = True
		if not valid_question(u_thirdopt):
			thirdopt_error = "Wrong type of answer in third option!"
			error = True
		if not valid_question(u_correct):
			correct_error = "Wrong type of correct answer!"
			error = True
		if not valid_question(u_theme):
			theme_error = "Wrong type of theme!"
			error = True
		if error:
			self.write_form(sani_question, sani_firstopt, sani_secondopt, sani_thirdopt,question_error, firstopt_error, secondopt_error, thirdopt_error,sani_correct,correct_error,sani_theme,theme_error)
		else:
			question= Question.query(Question.question==u_question).count()
			if question==0:
				q=Question()
				q.question=u_question
				q.first=u_firstopt
				q.second=u_secondopt
				q.third=u_thirdopt
				q.theme=u_theme
				q.correct=u_correct
				q.put()
				self.write_form()
				self.response.out.write ("<h3>Question: %s  added, add as many as you want</h3>" %u_question)
			else:
				self.write_form(sani_question, sani_firstopt, sani_secondopt, thirdopt_error,question_error, firstopt_error, secondopt_error, thirdopt_error)
				self.response.out.write ("<h3>Question: %s <p> was already inserted</h3>" %u_question)