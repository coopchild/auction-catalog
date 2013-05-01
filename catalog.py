#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import argparse
import codecs
import csv
import datetime
import itertools
import os
import re
import sys
from collections import OrderedDict
from jinja2 import evalcontextfilter, Environment, FileSystemLoader, Markup, escape
from operator import itemgetter
from pprint import pprint

# workaround for fun issues with printing unicode to stdout/terminal
reload(sys)
sys.setdefaultencoding("utf-8")

HTML_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates')

KNOWN_SECTIONS = [
    {"key":"D",
     "label":"Buy It Now",
     "closes":"6:30"},
    {"key":"A",
     "label":"Silent #1 - Red",
     "closes":"6:40"},
    {"key":"B",
     "label":"\"Uniquely Coop\" Silent - Black",
     "closes":"6:50"},
    {"key":"C",
     "label":"Silent #2 - White",
     "closes":"7:00"},
    {"key":"L",
     "label":"Live Auction",
     "closes":"9:30"},
]

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
 
    def __iter__(self):
        return self
 
    def next(self):
        return self.reader.next().encode("utf-8")
 
class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """
 
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.header = self.reader.next()
 
    def next(self):
        row = self.reader.next()
        vals = [unicode(s, "utf-8") for s in row]
        return dict((self.header[x], vals[x]) for x in range(len(self.header)))
 
    def __iter__(self):
        return self

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result     

def render_certs_to_html(certs):
    data = {}
    data['now'] = datetime.datetime.now()
    data['certs'] = certs
    jinja_env = Environment(
        loader = FileSystemLoader(HTML_TEMPLATE_DIR),
        extensions = []        
        )
    #jinja_env.globals.update()
    jinja_env.filters['nl2br'] = nl2br
    return jinja_env.get_template('certs.html').render(data)
        
def render_section_to_html(section):
    data = {}
    data['now'] = datetime.datetime.now()
    data['section'] = section
    jinja_env = Environment(
        loader = FileSystemLoader(HTML_TEMPLATE_DIR),
        extensions = []        
        )
    #jinja_env.globals.update()
    jinja_env.filters['nl2br'] = nl2br
    return jinja_env.get_template('catalog-section.html').render(data)

def build_catalog(rows, sectionize=True):
    # ensure data is sorted by ItemNum
    sorted_rows = sorted(rows, key=itemgetter('ItemNum'))
    
    ItemNums = []
    rows = []
    # remove duplicate TrackingNumber
    for row in sorted_rows:
        if row['TrackingNumber'] not in ItemNums:           
            # clean up character issues
            row['ItemDesc'] = row['ItemDesc'].replace(u"\r\n- ",u"\r\n\u2022 ")
            row['ItemDesc'] = row['ItemDesc'].replace(u"\r\n \x95",u"\r\n\u2022")
            row['ItemDesc'] = row['ItemDesc'].replace(u"\x95",u"\u2022")
            row['ItemDesc'] = row['ItemDesc'].replace(u"\x92",u"'")
            ItemNums.append(row['TrackingNumber'])
            rows.append(row)
    
    return rows        

def sectionize_catalog(rows):
    # return a list of items grouped by section?
    catalog = []
    for section in KNOWN_SECTIONS:
        section['auction_items'] = filter(lambda p: section['key'] == p['Auction'], rows)
        catalog.append(section)
    return catalog
    
def filter_certs(rows):
    return filter(lambda p: "1" == p['AuctCommCreateCert'], rows)

def main(args):
    f = open(args.catalog_file, 'rt')
    try:
        rows = UnicodeDictReader(f, encoding='iso-8859-2')
        
        catalog = build_catalog(rows)
        
        if args.mode == 'certs':            
            certs = filter_certs(catalog)            
            try:
                f = open('certs.html', "w")
                try:
                    f.write(render_certs_to_html(certs))
                finally:
                    f.close()
            except IOError:
                pass                
        else:
            catalog = sectionize_catalog(catalog)        
            # generate an HTML page for each catalog section
            for section in catalog:
                try:
                    file_name = "catalog-section-%s.html" % section['key']
                    f = open(file_name, "w")
                    try:
                        f.write(render_section_to_html(section))
                    finally:
                        f.close()
                except IOError:
                    pass
    finally:
        f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument('catalog_file', help='path to catalog Excel data')
    parser.add_argument('--mode', default='catalog', choices=['catalog','certs'])
    args = parser.parse_args()
    main(args)