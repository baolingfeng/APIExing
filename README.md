# APIExing
A tool for API Recognition and linking

# Pre-requisites

1. Python 2.7 with following packages: nltk, numpy, scikit-learn, gensim, html2text, beautifulsoup, Levenshtein, mysql.
2. <a href="http://www.chokkan.org/software/crfsuite/">crfsuite</a>
3. MySQL database

# API Recognition
## Preliminaries
First, we need convert a text file into a <a href="http://www.signll.org/conll/">CoNLL</a> file, which is widely used in Natural Language Processing (NLP). You can use python file **texttoconll.py** to convert text file into CoNLL file with the following command:
 > python texttoconll.py input.txt output.conll
 
## Data
1. The folder **apidoc**

*TODO*

2. The folder **data**

*TODO*

3. the folder **api_recog**: our experimental data for EMSE paper
  * **train_all.conll**: training data with manual label
  * **test_\*.all**: testing data

## Commands
1. convert a *CoNLL* file into an input file for *crfsuite*

> python enner.py bc-ce < api_recog/train_all.conll > api_recog/train_all.data

> python enner.py bc-ce < api_recog/test_all.conll > api_recog/test_all.data

2. learn a model using *crfsuite* 
> crfsuite learn -m model api_recog/train_all.data

3. use the trained model to test data
> crfsuite tag -m model -qt api_recog/test_all.data

# API Linking

## Overview
Given a post from Stack Overflow, we first crawle the content of the whole post web page including question, answers, comments, tags; then we use our API recogntion tool to identify API entities from the crawled text (exclude code fragment);
Finally, we link the idetified APIs to API documentations. 

See the corresponding python file **apilink.py**, you can run this file using following command:
> python apilink.py post_id output_file

## Data
1. the folder **mysql** contains two sql files, which are the API documents that we crawle from internet. There are four libraries: *matplotlib, numpy, pandas, matplotlib*. You need setup the database use the following steps:

* create a database schema *link_api*
* import the two sql files into the database
* change your database username and password in python file **apilink.py**

4. experimental data 
*TODO*



