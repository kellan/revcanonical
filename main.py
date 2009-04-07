#!/usr/bin/env python

#
# IANAPP (i am not a python programmer)
#


import cgi
import os
from sgmllib import SGMLParser

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import pprint

class MainPage(webapp.RequestHandler):

	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		if self.request.get('url'):
			template_values['url'] = self.request.get('url')
			
			try:
				links = RevCanonical().revcanonical(self.request.get('url'))
				
				if links:
					template_values['link'] = links[0]
				else:
					template_values['link'] = template_values['url']
			except Exception, e:
				template_values['error'] = e;
		
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		self.get()
		
	
class ApiPage(webapp.RequestHandler):
	def get(self):
		
		if self.request.get('url'):
			url = self.request.get('url')
			try:
				links = RevCanonical().revcanonical(self.request.get('url'))
				
				if links:
					url = links[0]
				
				self.response.out.write(url)
			except Exception, e:
				self.error(500)
				self.response.out.write(e)
		else:
			self.response.out.write("Takes argument <code>url</code> returns reverse canonicalized URL, if found.  Otherwise returns the passed URL.")
		
	def post(self):
		pass
		
class RevCanonical:	
	def revcanonical(self, url):
		resp = urlfetch.fetch(url)
		html = resp.content

		fragment = len(url.split('#')) > 1 and '#' + url.split('#')[1] or ''

		shorts = []
		
		parser = LinkParser()
		parser.feed(html)
		links = parser.links
			
		for l in links:
			for e in l:
				if e[0] == 'rel':
					if e[1].count('alternate') and e[1].count('short'):
						shorts.append(l)
					elif e[1].count('short_url'):
						shorts.append(l)
					elif e[1].count('shorter-alternative'):
						shorts.append(l)
				elif e[0] == 'rev':
					if e[1].count('canonical'):
						shorts.append(l)
			
		return self.hrefs(shorts, fragment)
	
	def hrefs(self, links, fragment = ''):
		hrefs = []
		for l in links:
			for e in l:
				if e[0] == 'href':
					hrefs.append(e[1] + fragment)

		return hrefs;

class LinkParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.links = []

    def do_link(self, attrs):
        hreflist = [e[1] for e in attrs if e[0]=='href']
        if hreflist:
            self.links.append(attrs)

    def end_head(self, attrs):
        self.setnomoretags()
    start_body = end_head

		
application = webapp.WSGIApplication( [('/', MainPage), ('/api', ApiPage)], debug=True)

def main():
	run_wsgi_app(application)


if __name__ == '__main__':
  main()
