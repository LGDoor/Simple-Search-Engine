'''
Created on 2013-4-12

@author: RaphaelYu
'''

import logging;
import codecs;

class Document():
    def __init__(self, title, content):
        self.title = title;
        self.content = content;

class AbstractDocumentManager(dict):

    def __init__(self, path):
        if path:
            self.load(path);
        
    def load(self, path):
        raise NotImplementedError;
    
    def add_doc(self, doc):
        doc_id = self.__generate_doc_id__(doc);
        self[doc_id] = doc;
    
    def get_id_by_title(self, title):
        for doc_id, doc in self.iteritems():
            if doc.title == title:
                return doc_id;
        return None;
    
    def __generate_doc_id__(self, doc):
        raise NotImplementedError;
    
class SimpleDocumentManager(AbstractDocumentManager):
    """
    Load documents from a single file separated by blank lines.
    The first of each document is the title and the rest is the content. 
    """
    def __init__(self, path):
        self._doc_id = 0;
        super(SimpleDocumentManager, self).__init__(path);
        
    def load(self, path):
        logging.info("Loading documents...");
        infile = codecs.open(path, encoding='utf-8');
        lines = [];
        while True:
            line = infile.readline();
            if (line == u"\n" or not line):
                if lines:
                    content = "".join(lines[1:]);
                    self.add_doc(Document(lines[0].rstrip(), content));
                    lines = [];
            else:
                lines.append(line);
            if not line:
                break;
        infile.close();
        logging.info("%d documents Loaded." % len(self));    
    
    def __generate_doc_id__(self, doc):
        doc_id = self._doc_id;
        self._doc_id += 1;
        return doc_id;