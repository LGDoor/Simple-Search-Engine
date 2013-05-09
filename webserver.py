'''
Created on 2013-4-12

@author: RaphaelYu
'''

import re;
import time;
import math;

import tornado.ioloop
from tornado import web;
from tornado import escape;
from tornado import template;

_RESULTS_PER_PAGE = 20;
_MAX_PAGE = 10;

class MainHandler(web.RequestHandler):
    def get(self):
        self.render("templates/main.html");

class QueryHandler(web.RequestHandler):
    """
    Handle the query with parameter 'q' and 'page'
    """
    def initialize(self, index, documents):
        self._index = index;
        self._documents = documents;
        self._template_loader = template.Loader("templates/", autoescape=None).load("query.html");
        
    def get(self):
        start_time = time.time();
        query = self.get_argument("q", "");
        if not query:
            self.redirect("/");

        page = self.get_argument("page", "");
        try:
            page = int(page);
        except:
            page = 1;

        terms = self._index.split(query);
                
        def generate_content(id_weight_tuple):
            matcher = re.compile("[^\W_]+", re.UNICODE);
            for doc_id, weight in id_weight_tuple:
                doc = self._documents[doc_id];
                ref = re.sub(" +", "_", doc.title);
                # simple excerpt
                content = escape.xhtml_escape(doc.content if len(doc.content) < 200 else doc.content[:200] + u"...");
                # highlight the keywords
                content = matcher.sub(lambda obj:u"<strong>" + obj.group(0) + u"</strong>" if obj.group(0).lower() in terms else obj.group(0), content);
                yield (doc.title, ref, content, weight);
        
        result = self._index.query(terms);
        number = len(result);
        # pagination
        n_pages = min(_MAX_PAGE, int(math.ceil(float(number) / _RESULTS_PER_PAGE)));
        page = min(n_pages, max(1, page));
        result = list(generate_content(result[20 * (page - 1) : 20 * page - 1]));
        
        elapsed_time = time.time() - start_time;
        
        self.write(self._template_loader.generate(**{
                 "result": result,
                 "query": query, 
                 "number":"{:,d}".format(number), 
                 "time":"%.3f" % elapsed_time,
                 "page": page,
                 "n_pages": n_pages
         }));
        self.flush();
        

def launch_web_server(index=None, documents=None):
    application = web.Application([
        (r"/", MainHandler),
        (r"/query", QueryHandler, dict(index=index, documents=documents)),
        (r"/res/(.*)", web.StaticFileHandler, {"path": "templates/res/"})
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    launch_web_server();