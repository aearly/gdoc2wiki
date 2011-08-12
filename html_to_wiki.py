#! /usr/bin/env python

import BeautifulSoup
import sys, css.parse

class NullDevice():
    def write(self, s):
        pass

def parse_contents(tag):
	#for c in tag.contents:
	#	parse_element(c)
	return "".join(map(parse_element, tag))

def parse_p(tag):
	return parse_span(tag) + "\n\n"

def parse_br(tag):
	return "\n"

def parse_h(tag):
	# add nothing but a newline if there is no text
	contents = parse_contents(tag)
	if contents == "":
		return "\n\n"

	tagName = tag.name
	level = int(tagName.replace("h",""))
	delim = "=" * level
	return delim + contents + delim + "\n\n"

def parse_span(tag):
	className = ""
	if tag.has_key("class"):
		className = tag["class"]
	italic = className in italicClasses
	code = className in codeClasses

	startDelim = ""
	endDelim = ""
	if code:
		startDelim = "<code>"
		endDelim = "</code>"
	elif italic:
		startDelim = "''"
		endDelim = "''"

	return startDelim + parse_contents(tag) + endDelim

def parse_ol(tag):
	ret = ""
	for c in tag.contents:
		ret += "#%s" % parse_element(c)

	return ret + "\n"

def parse_ul(tag):
	ret = ""
	for c in tag.contents:
		ret += "*%s" % parse_element(c)

	return ret + "\n"

def parse_li(tag):
	return " %s\n" % parse_span(tag)

def parse_a(tag):
	url = ""
	if tag.has_key("href"):
		url = tag["href"]

	if url == "":
		return parse_contents(tag)

	return "[%s %s]" % (url, parse_contents(tag))

tagMap = {
	"p" : parse_p,
	"br" : parse_br,
	"h1" : parse_h,
	"h2" : parse_h,
	"h3" : parse_h,
	"h4" : parse_h,
	"h5" : parse_h,
	"h6" : parse_h,
	"span" : parse_span,
	"ol" : parse_ol,
	"ul" : parse_ul,
	"li" : parse_li,
	"a" : parse_a
}

def parse_tag(tag):
	tagName = tag.name
	if tagMap.has_key(tagName):
		return tagMap[tagName](tag)

	return ""

def parse_element(elem):
	if isinstance(elem, BeautifulSoup.NavigableString) and elem != None:
		elemStr = str(elem)
		if "[" in elemStr:
			return "<nowiki>%s</nowiki>" % elemStr
		return elemStr
	elif isinstance(elem, BeautifulSoup.Tag):
		return parse_tag(elem)
	

inFileName = sys.argv[1]
inFile = open(inFileName, "r")

soup = BeautifulSoup.BeautifulSoup( inFile.read() )

# print soup.prettify()

# get styles
styleTag = soup.html.head.style;

#redirect output during parsing
sys.stdout = NullDevice()

styles = css.parse.parse(styleTag.contents[0])

sys.stdout = sys.__stdout__

# grab some important class names from the style declarations
codeClasses = []
italicClasses = []

for rule in styles:
	for decl in rule:
		if "Courier New" in str(decl.value):
				codeClasses.append(rule.selectors[0].replace(".",""))
		if "italic" in str(decl.value):
				italicClasses.append(rule.selectors[0].replace(".",""))

print parse_contents(soup.html.body)