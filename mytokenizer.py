# -*- coding: utf-8 -*-
'''
our tokenizer
'''

import sys
# import os
import twokenize

def tokenize(istring, ostring):
    # print 'this is mytokenizer.py
    ifile = open(istring, 'r')
    ofile = open(ostring, 'w')
    for line in ifile:
        try:
            ofile.write(u" ".join(twokenize.tokenize(
                line[:])).encode('utf-8') + '\n')
        except:
            print line
    ofile.close()
    ifile.close()


def tokenize_str(istring):
    ostring = []
    for line in istring.split('\n'):
        try:
            ostring.append(
                u" ".join(twokenize.tokenize(line[:])).encode('utf-8'))
        except Exception as e:
            print e
            print line

    return '\n'.join(ostring)


if __name__ == '__main__':
    try:
        tokenize(*sys.argv[1:])
    except TypeError:
        print "Usage : python tokenize.py <input file> <output file>"
        print "See README for input file format"
