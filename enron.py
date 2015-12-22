import threading
import os
import thread
from classify import Classifier
import re
import sys
from stop_words import STOP_WORDS

def load_classifier():
    if not os.path.exists('classifier.db'):
        #refreshing if not exists
       classifier=train('corpus')
       classifier.save('classifier.db')
       return classifier

    else:
        return Classifier.load('classifier.db')

def extract_features(s, min_len=2, max_len=20):

    words = []
    for w in s.lower().split():
        wlen = len(w)
        #if w not in StopWordsList():
        if w not in STOP_WORDS and wlen > min_len and wlen < max_len:
                words.append(w)
    return words

def email_extract(subject,To,From, body, min_len=2, max_len=20):
    """
    Handle a subject and body and extract the features correctly
    """
    terms = ['s:%s' % w for w in extract_features(subject, min_len, max_len)]
    To= ['t:%s' % w for w in extract_features(To, min_len, max_len)]
    From= ['f:%s' % w for w in extract_features(From, min_len, max_len)]
    terms+=To
    terms+=From
    terms.extend(extract_features(body, min_len, max_len))
    return terms

def enron_email_extract(text, min_len=2, max_len=20):

    lines = []
    subj = ''
    to=''
    fr=''
    for line in text.splitlines():
        if line.startswith('subject:'):
            is_subj = True
            subj = line[8:]
        elif line.startswith('To:'):
            is_To=True
            to=line[3:]
        elif line.startswith('From:'):
            is_From=True
            fr=line[5:]

        else:
            lines.append(line)
    return email_extract(subj,to,fr, ' '.join(lines), min_len, max_len)

###############################################alternative solution
def extract_features2(s):
        words=[]
        c=(filter (lambda x:re.match("^[a-zA-Z]+$",x),[x for x in set(re.split("[\s:/,.:]",s))]))
        for w in c:
            words.append(w)
        return words
################################################
def train(corpus='corpus'):
    classifier = Classifier()
    curdir = os.path.dirname(__file__)
    spam_dir = os.path.join(curdir, corpus, 'spam')
    ham_dir = os.path.join(curdir, corpus, 'ham')
 
    train_classifier(classifier, spam_dir, 'spam')
    train_classifier(classifier, ham_dir, 'ham')

    #alternative -- use threads for speed
    '''threads=[]
    for i in range(0,2):
        t=threading.Thread(target=train_classifier,args=(classifier,[spam_dir,ham_dir][i],['spam','ham'][i]))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()'''
 
    return classifier
 
def train_classifier(classifier, path, label):


    for filename in os.listdir(path):
        with open(os.path.join(path, filename)) as fh:
            contents = fh.read()
 
        # extract the words from the document
        features = enron_email_extract(contents)
 
        # train the classifier to associate the features with the label
        classifier.train(features, [label])

    

def test(classifier, corpus='corpus2'):
    curdir = os.path.dirname(__file__)
 
    spam_dir = os.path.join(curdir, corpus, 'spam')
    ham_dir = os.path.join(curdir, corpus, 'ham')
 
    correct = total = 0
 
    for path, label in ((spam_dir, 'spam'), (ham_dir, 'ham')):
        for filename in os.listdir(path):
            with open(os.path.join(path, filename)) as fh:
                contents = fh.read()
 
            # extract the words from the document
            features = enron_email_extract(contents)
 
            results = classifier.classify(features)
 
            if results[0][0] == label:
                correct += 1
            total += 1
 
    pct = 100 * (float(correct) / total)
    print '[%s]: processed %s documents, %02f%% accurate' % (corpus, total, pct)

def testUnKnownDirectory(classifier,corpus):
    curdir = os.path.dirname(__file__)
    path=os.path.join(curdir, corpus,"UnKnownDir")
    for filename in os.listdir(path):
            with open(os.path.join(path, filename)) as fh:
                contents = fh.read()

            features = enron_email_extract(contents)

            results = classifier.classify(features)
            print "guess : {0} \t For File : {1}".format(results[0][0],filename)

def testSomeFile(classifier, corpus):
    curdir = os.path.dirname(__file__)
    spam_dir = os.path.join(curdir, corpus, 'spam')
    ham_dir = os.path.join(curdir, corpus, 'ham')
    correct = total = 0
 
    for path, label in ((spam_dir, 'spam'), (ham_dir, 'ham')):
        for filename in os.listdir(path):
            with open(os.path.join(path, filename)) as fh:
                contents = fh.read()
 
            # extracting
            features = extract_features(contents)
 
            results = classifier.classify(features)
            print "guess : {0} \t while : {1}".format(results[0][0],label)
            if results[0][0] == label:
                correct += 1
            total += 1
    pct = 100 * (float(correct) / total)
    print '[%s]: processed %s documents, %02f%% accurate' % (corpus, total, pct)
    
            
if __name__ == '__main__':
    #input=raw_input("enter corpuses seprated by space:")
    #corpus=input.split()
    corpus=['corpus2','corpus3','m_corpus2']
    classifier=load_classifier() #recreated if not exists
    threads=[]
    for i in range(0,len(corpus)):
        thread=threading.Thread(target=test,args=(classifier, corpus[i]))
        threads.append(thread)
    for th in threads:
         th.start()
    for th in threads:
        th.join()
    #test(classifier, 'corpus2')
    #test(classifier, 'corpus3')
    #testSomeFile(classifier,'m_corpus2')
    testUnKnownDirectory(classifier,'m_corpus')



    

