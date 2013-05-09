'''
Created on 2013-4-9

@author: RaphaelYu
'''

from indexer import Indexer;
from document import SimpleDocumentManager;
from webserver import launch_web_server;
import logging;
import codecs;

def load_stop_words(filename):
    logging.info("Loading stop words...");
    stop_words = set();
    infile = codecs.open(filename, encoding="utf-8");
    for line in infile:
        stop_words.add(line.rstrip().lower());
    infile.close();
    return stop_words;

def print_result(result):
    # for debug only
    for doc_id, weight in result:
        print "%s: %f" % (documents[doc_id].title, weight); 

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO);

    stop_words_set = load_stop_words("stop_words.txt");
    documents = SimpleDocumentManager("corpus.txt");
    index = Indexer(documents, stop_words_set);
    
    launch_web_server(index, documents);
    pass;