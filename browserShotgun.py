#!/usr/bin/env python
import sys
from urllib import parse
import urllib.request

from html.parser import HTMLParser

class ParsePDFLink(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.current_attrs = None
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.current_attrs = ParsePDFLink.attrs_to_dict(attrs)

    def handle_endtag(self, tag):
        self.current_tag = None
        self.current_attrs = None

    def handle_data(self, data):
        if self.current_tag == 'a':
            href = self.current_attrs['href']
            if href.endswith('.pdf') and data == 'the current browser graphic in PDF':
                print(href)

    def attrs_to_dict(attr_list_of_tuples):
        d = {}
        for k,v in attr_list_of_tuples:
            d[k] = v
        return d

def parsed_position_to_str(*parsed):
    if type(parsed[0]) == type([]):
        parsed = parsed[0]
    return "%s:%d-%d" % (parsed[0],parsed[1],parsed[2])
def flatten_lists(d):
    d_out = {}
    for k,v in d.items():
        d_out[k] = v[0]
    return d_out

def parse_position_str(ps):
    # as in 'chrIII:4036199-4043918'
    chrom,genomic_range = ps.split(':')
    s,e = map(int, genomic_range.split('-'))
    return chrom,s,e

url = sys.argv[1] # https://genome.ucsc.edu/cgi-bin/hgTracks?db=ce11&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=chrIII%3A4036199%2D4043918&hgsid=1491000571_vauCeWsWTJeFt529VIOU9i1ZzGVU

parsed_url = parse.urlparse(url)
parsed_query = flatten_lists( parse.parse_qs(parsed_url.query) )
print(parsed_query)
print( parse_position_str( parsed_query['position'] ))

# https://genome.ucsc.edu/cgi-bin/hgTracks?hgsid=1491000571_vauCeWsWTJeFt529VIOU9i1ZzGVU&hgt.psOutput=on

with open('random_10_promoters_seed0.bed') as bedfile:
    for line in bedfile:
        fields = line.strip().split()
        chrom = fields[0]
        start = int(fields[1])
        end = int(fields[2])

        position = parsed_position_to_str(chrom, start, end)
        parsed_query['position'] = position
        parsed_query['hgt.psOutput'] = 'on'
        print(parsed_query)
        newquery = parse.urlencode(parsed_query)
        pdf_page_link = parse.urlunsplit([parsed_url.scheme, parsed_url.netloc, parsed_url.path, newquery,parsed_url.fragment])
        pdf_page_html = str(urllib.request.urlopen(pdf_page_link).read())
        htmlParser = ParsePDFLink()
        htmlParser.feed(pdf_page_html)
        #print(pdf_page_html)
