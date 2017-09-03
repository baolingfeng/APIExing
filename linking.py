# -*- coding: utf-8 -*-

import os
import subprocess
import re
import string
import urlparse
from multiprocessing import Pool
from lxml import etree
from datetime import datetime
import collections
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
import Levenshtein
from bs4 import BeautifulSoup
from html2txt import html2txt
import texttoconll
import requests
import mytokenizer
from dbimpl import DBImpl
import twokenize


STATIC_ROOT = './'
POST_DIR = './posts/'


dbimpl = DBImpl({"type": "mysql", "url": "127.0.0.1", "username": "root",
                 "password": "123456", "database": "link_api"})

token_list = {}


def query_records(value):
    sql = 'select * from link_api_record where name = %s'

    return dbimpl.querymany(sql, value)

def query_web_cache(link):
    sql = 'select * from web_cache where url = %s'

    return dbimpl.queryone(sql, link)

def api_recog(post_id, post_text):
    txt_file = post_id + '.txt'
    conll_file = post_id + '.conll'
    data_file = post_id + '.data'
    label_file = post_id + '.label'
    with open(os.path.join(POST_DIR, txt_file), 'w') as f:
        f.write(mytokenizer.tokenize_str(post_text))

    texttoconll.main(os.path.join(POST_DIR, txt_file),
                     os.path.join(POST_DIR, conll_file))

    extract_feature_cmd = "python " + os.path.join(STATIC_ROOT, 'enner.py') + " bc-ce < " + os.path.join(
        POST_DIR, conll_file) + " > " + os.path.join(POST_DIR, data_file)
    subprocess.call(extract_feature_cmd, shell=True)

    crfsuite_cmd = "crfsuite tag -m " + os.path.join(STATIC_ROOT, 'model_all') + " " + os.path.join(
        POST_DIR, data_file) + " > " + os.path.join(POST_DIR, label_file)
    subprocess.call(crfsuite_cmd, shell=True)

    output = []
    with open(os.path.join(POST_DIR, conll_file)) as fconll:
        flabel = open(os.path.join(POST_DIR, label_file))
        labels = [line.strip() for line in flabel.readlines()]

        lines = fconll.readlines()
        print len(labels), len(lines)
        for idx, line in enumerate(lines):
            if idx > len(lines) - 2:
                break

            if line.strip() == '':
                w = t = ''
            else:
                w, t = line.strip().split('\t')

            if lines[idx + 1].strip() == '':
                w2 = t2 = ''
            else:
                w2, t2 = lines[idx + 1].strip().split('\t')

            if labels[idx] == 'B-API':
                output.append((w, w2))
        flabel.close()

    return output


def parse_post(post_id):
    data = {}
    hrefs = []
    full_texts = []
    texts_without_code = []

    url = 'http://stackoverflow.com/questions/%s' % post_id
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    e = soup.find("div", {"id": "question-header"})
    title_a = e.find("a", {"class": "question-hyperlink"})
    data['title'] = title_a.text

    full_texts.append(title_a.text)
    texts_without_code.append(title_a.text)

    # get the text from question
    question_div = soup.find("div", {"class": "question"})
    post_div = question_div.find("div", {"class": "post-text"})

    class_parsed_list = []
    for e in post_div:
        full_texts.append(str(e.encode('utf-8')))
        if e.name != 'pre':
            texts_without_code.append(str(e.encode('utf-8')))
            # texts_without_code.append(e)
        else:
            code = html2txt(str(e.encode('utf-8'))).lower()
            m = re.search(r'class (\S+):', code)
            if m:
                cls = m.group(1)
                idx = cls.find('(')
                if idx >= 0:
                    cls = cls[0:idx].strip()
                class_parsed_list.append(cls)

    for e in post_div.find_all("a"):
        hrefs.append(e['href'])

    comment_div = question_div.find("div", {"class": "comments"})
    if comment_div is not None:
        comments = comment_div.find_all("span", {"class": "comment-copy"})
        for e in comments:
            full_texts.append(str(e.encode('utf-8')))
            texts_without_code.append(str(e.encode('utf-8')))
            # full_texts.append(e)
            # texts_without_code.append(e)

            for link in e.find_all("a"):
                hrefs.append(link['href'])

    # get the text from answers
    answer_div = soup.find_all('div', {"class": "answer"})
    for answer in answer_div:
        answer_posts = answer.find_all("div", "post-text")
        for post in answer_posts:
            for e in post:
                full_texts.append(str(e.encode('utf-8')))
                # full_texts.append(e)
                if e.name != 'pre':
                    texts_without_code.append(str(e.encode('utf-8')))
                    # texts_without_code.append(e)
                else:
                    code = html2txt(str(e.encode('utf-8'))).lower()
                    m = re.search(r'class (\S+):', code)
                    if m:
                        cls = m.group(1)
                        idx = cls.find('(')
                        if idx >= 0:
                            cls = cls[0:idx].strip()
                        class_parsed_list.append(cls)

            for e in post.find_all("a"):
                hrefs.append(e['href'])

            comment_div = answer.find("div", {"class": "comments"})
            if comment_div is not None:
                comments = comment_div.find_all(
                    "span", {"class": "comment-copy"})
                for e in comments:
                    full_texts.append(str(e.encode('utf-8')))
                    texts_without_code.append(str(e.encode('utf-8')))

                    for link in e.find_all("a"):
                        hrefs.append(link['href'])

    text_to_link = '\n'.join([html2txt(t)
                              for t in texts_without_code if html2txt(t) != ""])

    entities = api_recog(post_id, text_to_link)

    data['texts'] = '\n'.join([html2txt(t)
                               for t in full_texts if html2txt(t) != ""])

    taglist = []
    for e in soup.find("div", {"class": "post-taglist"}):
        tag = html2txt(str(e.encode('utf-8')))
        if tag.strip() != "":
            taglist.append(tag)

    data['tags'] = taglist
    data['class_parsed_list'] = class_parsed_list
    data['hrefs'] = hrefs

    entityList = []
    entityIndex = []
    pre_entity = None
    idx = 0
    for api in entities:
        # print api
        for n in range(idx, len(full_texts)):
            text = html2txt(full_texts[n]).lower()
            temp = mytokenizer.tokenize_str(text)
            arr = temp.split(' ')

            if n == idx and pre_entity == api[0]:
                # print arr, api[0], idx
                idx2 = arr.index(api[0])
                arr = arr[idx2 + 1:]

            if api[0] in arr:
                idx2 = arr.index(api[0])
                if arr[idx2 + 1] == api[1]:
                    entityList.append(api[0])
                    entityIndex.append(n)

                    idx = n
                    break

        pre_entity = api[0]

    print entityList
    print entityIndex
    data['entityList'] = entityList
    data['entityIndex'] = entityIndex
    return data


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def lemma_tokens(tokens, lmtzr):
    lemmatized = []
    for item in tokens:
        lemmatized.append(lmtzr.lemmatize(item))
    return lemmatized


def tokenize(text):
    stemmer = PorterStemmer()
    # lmtzr = WordNetLemmatizer()
    tokens = twokenize.tokenize(text)
    tokens_clean = [s for s in tokens if s not in set(string.punctuation)]
    # tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens_clean, stemmer)
    return stems

def extract_txt(url, idx, insert):
    print url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    body = soup.find("div", {"class": "body"})
    if body is None:
        body = soup.find('body')

    return (idx + 1, body.text, url, insert)

def log_result(result):
    token_list[result[0]] = result[1]

    print result[0], result[2], result[3]
    if not result[3]:
        sql = 'update web_cache set content=%s, access_time=%s where url=%s'
        dbimpl.updateone(sql, result[1], datetime.now(), result[2])
    else:
        sql = 'insert web_cache(url, content) values(%s, %s)'
        dbimpl.updateone(sql, result[2], result[1])

def crawl(links, token_list):
    p = Pool()
    for idx, record in enumerate(links):
        web_entry = query_web_cache(record)
        if web_entry is None:
            p.apply_async(extract_txt, args=(
                record, idx, True), callback=log_result)
        else:
            # print 'days', web_entry[3], web_entry[3] - datetime.now(),
            # (web_entry[3] - datetime.now()).days
            interval = datetime.now() - web_entry[3]
            # print 'days', interval.days
            if interval.days > 30:
                p.apply_async(extract_txt, args=(
                    record, idx, False), callback=log_result)
            else:
                token_list[idx + 1] = web_entry[2]

    p.close()
    p.join()

def link_entity(data):
    print 'Begin Entity Linking'

    data_entity = data["entityList"]
    data_entity_index = data["entityIndex"]
    class_parsed_list = data["class_parsed_list"]
    question_title = re.findall(r"[\w']+", data["title"].lower())
    tag_list = [x.lower() for x in data["tags"]]
    href_list = [x.lower() for x in data["hrefs"]]
    encode_texts = data["texts"].encode('ascii', errors='xmlcharrefreplace')
    full_text = encode_texts.translate(None, string.punctuation)

    variations = {'np': 'numpy', 'mpl': 'matplotlib', 'pd': 'pandas',
                  'fig': 'figure', 'plt': 'pyplot', 'bxp': 'boxplot', 'df': 'dataframe'}
    import_variations = {}
    declare_variations = {}

    # print encode_texts
    m = re.findall(r'import (\S+) as (\S+)', encode_texts)
    if (m):
        import_variations = dict((y, x) for x, y in m)

    n = re.findall(r'(\w+)\s?=\s?([A-Za-z0-9_\.]+)\(', encode_texts)
    if (n):
        declare_variations = dict((x, y) for x, y in n)

    variations.update(import_variations)
    variations.update(declare_variations)
    print variations

    href_info = []
    result_list = []
    class_list = []
    qualified_entity_list = []

    for href in href_list:
        temp = {}
        o = urlparse.urlsplit(href.encode('ascii', 'ignore').strip().lower())
        temp['domain'] = o.netloc
        temp['file'] = o.path.rsplit('/', 1)[-1]
        href_info.append(temp)

    for idx, entity in enumerate(data_entity):
        for k, v in variations.iteritems():
            entity = re.sub(r'^%s\.' % k, v + '.', entity).strip('?:!.,;')

        records = query_records(entity)

        if len(records) == 0:
            continue
        elif len(records) == 1:
            qualified_entity_list.append(entity)
            if records[0][5] == "class":
                class_list.append((entity, data_entity_index[idx]))
        else:
            result_sublist = []
            for idx, record in enumerate(records):
                mark = [False] * 3
                result = {}

                a = record[2].lower()
                r = urlparse.urlsplit(a.encode('ascii', 'ignore').strip())

                for link in href_info:
                    if(link['domain'] == r.netloc and link['file'] == r.path.rsplit('/', 1)[-1]):
                        mark[0] = True

                if record[3] in tag_list:
                    mark[1] = True

                if record[3] in question_title:
                    mark[2] = True

                result['score'] = sum(b << i for i, b in enumerate(mark))
                result['name'] = entity
                result['type'] = record[4]
                result_sublist.append(result)

            maxScoreResult = max(result_sublist, key=lambda x: x['score'])
            if maxScoreResult['type'] == 'class':
                class_list.append(
                    (maxScoreResult['name'], data_entity_index[idx]))
    class_list = class_list + class_parsed_list
    print class_list

    qualified_entity_list = set(qualified_entity_list)

    for curr_key, entity in enumerate(data_entity):
        print entity
        for k, v in variations.iteritems():
            entity = re.sub(r'^%s\.' % k, v + '.', entity).strip('?:!.,;')

        records = query_records(entity)

        if len(records) == 0:
            print 'No records are found in database'
            result_list.append([])
            continue
        elif len(records) == 1:
            print 'Only one record is found in database'
            record = records[0]
            result = [{}]
            result[0]['name'] = entity
            result[0]['type'] = record[5]
            result[0]['url'] = record[2]
            result[0]['lib'] = record[4]
            result_list.append(result)
        else:
            print '%d records are found in database' % len(records)
            result_sublist = []

            ####### tf-idf ##########
            links = []
            tdidf_result = []
            for record in records:
                links.append(urlparse.urlsplit(
                    record[2].encode('ascii', 'ignore').strip()).geturl())

            token_list.clear()
            token_list_sorted = []

            token_list[0] = full_text
            crawl(links, token_list)

            token_od = collections.OrderedDict(sorted(token_list.items()))

            for item in token_od.itervalues():
                token_list_sorted.append(item)

            tfidf = TfidfVectorizer(
                tokenizer=tokenize, stop_words='english', ngram_range=(1, 1))
            tfs = tfidf.fit_transform(token_list_sorted)

            tdidf_result = (tfs * tfs.T).A[0]
            # print tdidf_result

            for idx, record in enumerate(records):
                mark = [False] * 5
                result = {}

                # url
                a = record[2].lower()
                r = urlparse.urlsplit(a.encode('ascii', 'ignore').strip())

                for link in href_info:
                    if(link['domain'] == r.netloc and link['file'] == r.path.rsplit('/', 1)[-1]):
                        mark[0] = True

                # qualified name match
                full_name = record[5] + '.' + record[1]
                for e in qualified_entity_list:
                    if (full_name in e):
                        mark[1] = True

                # tag
                if record[3] in tag_list:
                    mark[2] = True

                # title
                if record[3] in question_title:
                    mark[3] = True

                # class
                result['distance'] = -1
                temp = []
                for valid_class in class_list:
                    if Levenshtein.ratio(valid_class[0], record.api_class) > 0.8:
                        mark[4] = True
                        temp.append(
                            abs(data_entity_index[int(curr_key)] - valid_class[1]))

                if mark[4]:
                    result['distance'] = min(temp)

                result['mark'] = mark
                result['api_class'] = record[5]
                result['score'] = sum(
                    b << i for i, b in enumerate(reversed(mark)))
                result['name'] = entity
                result['url'] = record[2]
                result['lib'] = record[3]
                result['type'] = record[4]
                result['tfidf'] = str(tdidf_result[idx + 1])
                result_sublist.append(result)

            minDistanceResult = 0
            try:
                minDistanceResult = min(
                    (x for x in result_sublist if x['distance'] >= 0), key=lambda x: x['distance'])
            except (ValueError, TypeError):
                pass

            if minDistanceResult:
                i = result_sublist.index(minDistanceResult)
                result_sublist[i]['score'] = result_sublist[i]['score'] + 1

            result_list.append(result_sublist)
    
    for idx, linked_apis in enumerate(result_list):
        print data_entity[idx]

        for api in linked_apis:
            print api['name'], api['url'], api['score']



if __name__ == '__main__':
    post_id = '35782929'
    data = parse_post(post_id)

    link_entity(data)

    dbimpl.close()
