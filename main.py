#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment (loader = jinja2.FileSystemLoader (template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str (self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render (self, template, **kw):
    self.write(self.render_str(template, **kw))

class Entry(db.Model):  #creates an entity
  title = db.StringProperty(required = True) #constraint, won't let you NOT enter a title
  entry = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True) #set created at current time when entry is created
  #all this in google docs for datastore

class Blog(Handler):
  def render_blog(self, title="", entry=""):

    entrys = db.GqlQuery("SELECT * FROM Entry \
                        ORDER BY created DESC LIMIT 5")

    self.render("blog.html", title= title, entry= entry, entrys=entrys)

  def get (self):
    self.render_blog()

  def post (self):
    title = self.request.get("title")
    entry = self.request.get("entry")


class NewPost(Handler):
  def render_new_post(self, title="", entry="", error=""):
    self.render("new-post.html", title=title, entry=entry, error=error)

  def get (self):
    self.render_new_post()

  def post (self):
    title = self.request.get("title")
    entry = self.request.get("entry")

    if title and entry:
      e = Entry(title = title, entry = entry)
      #creates new instance of entry
      e.put()
      #stores new entry object in database
      self.redirect("/blog/%s" % str (e.key().id()))

    else:
      error = "You must enter BOTH a title AND a blog post. Please try again."
      self.render_new_post(title, entry, error)


class ViewPost(Handler):

    def get(self, id):
        post = Entry.get_by_id( int(id) )

        if post:
            self.render("view-individual-post.html", title = post.title, entry = post.entry)
        else:
            error= "Sorry, the post you requested does not exist. Please try again."
            self.render("view-individual-post.html", error = error)

app = webapp2.WSGIApplication([
('/', Blog),
('/blog', Blog),
('/newpost', NewPost),
webapp2.Route('/blog/<id:\d+>', ViewPost),
], debug =True)
