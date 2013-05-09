'''
Created on 2013-4-10

@author: RaphaelYu
'''

from collections import Counter;
import re;
import math;
import logging;
from porterstemmer import Stemmer;

_TERM_PATTERN = "[^\W_]+";

class DocIndexNode():
    def __init__(self, doc_id, counter, n_terms):
        self.doc_id = doc_id;
        self.counter = counter;
        self.n_terms = n_terms;

class InvIndexNode():
    def __init__(self, doc_id, weight):
        self.doc_id = doc_id;
        self.weight = weight;

class Indexer():
    def __init__(self, documents, stop_words):
        '''
        Constructor
        '''
        
        self.doc_index = {};
        self.inv_index = {};
        self._stemmer = Stemmer();
        self._documents = documents;
        self._stop_words = frozenset(self._stemmer(word.lower()) for word in stop_words);
        self._re = re.compile(_TERM_PATTERN, re.UNICODE);
        
        logging.info("Creating documents index...");
        for doc_id, doc in self._documents.iteritems():
            self._create_documents_index(doc_id, doc.content);
        
        logging.info("Creating inverted index...");
        self._create_inverted_index();
        logging.info("Indexing finished. %d term nodes are created." % len(self.inv_index))
    
    def split(self, query):
        """
        Extract the terms from the raw query.
        """
        return self._re.findall(query.lower());    
    
    def query(self, term_list, top_k=None):
        """
        """
        result = self._conjunctive_query(term_list);
        re_list = result.most_common(top_k);
        return re_list;        
    
    def _conjunctive_query(self, term_list):
        """
        Take the intersection result of multiple keywords and add their weights.
        """
        result = Counter();
        terms = [self._stemmer(term.lower()) for term in term_list if term not in self._stop_words];
        if not terms:
            return result; 
        counters = [Counter(self._single_query(term)) for term in terms];
        addition = reduce(lambda x,y:x+y, counters);
        intersection = reduce(lambda x,y:x&y, counters);
        for key in intersection.iterkeys():
            result[key] = addition[key];
        return result;    
    
    def _single_query(self, term):
        return self.inv_index.get(term, {});

    def _create_documents_index(self, doc_id, content):
        terms = self._re.findall(content);            
        counter = Counter(filter(lambda term: term not in self._stop_words,
                                  (self._stemmer(term.lower()) for term in terms)));
        self.doc_index[doc_id] = DocIndexNode(doc_id, counter, sum(counter.values()));
 
        
    def _create_inverted_index(self):
        # tf
        for doc_id, doc_node in self.doc_index.iteritems():
            for term, count in doc_node.counter.iteritems():
                if (term not in self.inv_index):
                    self.inv_index[term] = {};
                self.inv_index[term][doc_id] = float(count)/doc_node.n_terms;
                
        # tf-idf
        n_doc = float(len(self._documents));
        for inv_doc_list in self.inv_index.itervalues():
            for doc_id in inv_doc_list.iterkeys():
                inv_doc_list[doc_id] *= math.log(n_doc/len(inv_doc_list));

if __name__ == "__main__":
    index = Indexer(None, None);
    pass;