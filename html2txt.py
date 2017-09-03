# -*- coding: utf-8 -*-

import re
from HTMLParser import HTMLParser
from htmlentitydefs import entitydefs

mycompile = lambda pat:  re.compile(pat,  re.UNICODE)
WS_RE = mycompile(r'  +')

Url_new = r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))"""
AtMention = r'@[a-zA-Z0-9_]+'

def squeeze_whitespace(s):
    new_string = WS_RE.sub(" ",s)
    return new_string.strip()

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        self.entityref = re.compile('&[a-zA-Z][-.a-zA-Z0-9]*[^a-zA-Z0-9]')

    def handle_data(self, d):
        self.fed.append(d)

    def handle_starttag(self, tag, attrs):
        self.fed.append(' ')

    def handle_endtag(self, tag):
        self.fed.append(' ')

    def handle_entityref(self, name):
        if entitydefs.get(name) is None:
            m = self.entityref.match(self.rawdata.splitlines()[self.lineno-1][self.offset:])
            entity = m.group()
            # semicolon is consumed, other chars are not.
            if entity is not None:
            	#print "entity is none"
                if entity[-1] != ';':
                    entity = entity[:-1]
                self.fed.append(entity)
            else:
                self.fed.append('')
        else:
            self.fed.append(' ')

    def get_data(self):
        self.close()
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    html = re.sub(r'<code>', '`', html)
    html = re.sub(r'</code>', '`', html)
    html = re.sub(r'&#xA;&#xA;<pre.*?>.*?</pre>', '#CODE', html) # add .*? to match tag class
    html = re.sub(r'<pre.*?>.*?</pre>', '#CODE', html) # add this line to handle code snippet only posts. 
    #html = re.sub(r'(`(?=\S)|(?<=\S)`)', '', html)
    html = re.sub(r'(&#xA;)+','\n', html)
    s.feed(html)
    return s.get_data()

def my_encoder(my_string):
    for i in my_string:
        try:
            yield unicode(i, 'utf-8')
        except UnicodeDecodeError:
            yield ' ' # or another whitespaces

def html2txt(content):
    try:
        pro = ''.join( my_encoder( strip_tags(content) ) )
        pro = re.sub(r'^ +', '', pro)
        pro = re.sub(r'\n +', '\n', pro)
        pro = re.sub(r'[\n]+', '\n',pro)
        pro = squeeze_whitespace(pro)
        #pro = re.sub(Url_new, '#URL', pro, flags=re.DOTALL)
        pro = re.sub(AtMention, '@USER', pro)
        return pro
    except Exception as e:
        return content
    