#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# This script can update the title page from any RSS feed, but concrete
# adjustments are done specifically to Fedora Planet.
#
# It replaces the content between <!-- BLOG_HEADLINES_START -->
# and <!-- BLOG_HEADLINES_END --> in _site/index.html. The file
# path of index.html can be passed as an argument.
#
# Usage:
#
#   ./rss.py _site/index.html

from __future__ import print_function
import codecs
import os
import sys
import feedparser
import re
import sys

feedparser._HTMLSanitizer.unacceptable_elements_with_end_tag.add('<div>')

defenc = "utf-8" if sys.getdefaultencoding() == "ascii" else sys.getdefaultencoding()

FedMag = ['http://fedoraplanet.org/rss20.xml']

if len(sys.argv) > 2:
    print ('Alone script or only one argument is allowed.')
    sys.exit(1)

HTML = u"""
"""


for feed in map(feedparser.parse, FedMag):
    # We will parse last ten items
    HTML += u"""
<div class="container" id="blog-headlines">
    <div class="container">
    <div class="row">
      <div class="col-sm-12">
          <h2><span>Fedora Planet</span></h2>
      </div>
    </div>
    <div class="row">
"""
    cnt = 0
    # Getting at least 4 items in case of some python exceptions.
    for item in feed["items"][:6]:
        if int(cnt) % 2 == 0:
            HTML += u"""
    <div class="col-sm-6 blog-headlines">
    """
        item.title = item.title.replace("&", "&#38;")
        author, title = item.title.split(':', 1)
        link = item.links[0]['href']
        # Remove image tag from beginning
        try:
            article_desc = '\n'.join(item.description.split('\n')[1:])
            # remove html tags from description
            article_desc = re.sub('<[^<]+?>', '', article_desc)
            article_desc = re.sub('<', '&lt;', article_desc)
            article_desc = re.sub('>', '&gt;', article_desc)
            if len(article_desc) > 140:
                article_desc = ' '.join(article_desc.split()[0:25]) + '...'
            if not article_desc.startswith('<p>'):
                article_desc = '<p>%s</p>' % article_desc
        except AttributeError:
            print ('AttributeError. Going to next item')
            continue
        # we got
        # Tue, 20 Oct 2015 03:28:42 +0000
        # But we expect
        # Tue, 20 Oct 2015
        article_date = ' '.join(item.updated.split()[:4])
        HTML += u"""
        <article>
        <h3><a href="{article_url}">{article_title}</a></h3>
        {article_desc}
        <p><a href="{article_url}">Read more</a></p>
        <p class="byline">by <span class="author">{author}</span> <span class="date">{article_date}</span></p>
        </article>
""".format(article_url=link,
           article_title=title,
           article_desc=article_desc,
           article_date=article_date,
           author=author)
        cnt += 1
        if int(cnt) % 2 == 0:
            HTML += u"""
    </div>
"""
        # Condition if items were collected properly
        if int(cnt) > 3:
            break
    HTML += u"""
</div>
</div>
</div>
"""

if len(sys.argv) == 1:
    INDEX_FILE = os.path.join('.', '_site', 'index.html')
else:
    INDEX_FILE = sys.argv[1]
with codecs.open(INDEX_FILE, 'r', 'utf8') as f:
    contents = [line for line in f.readlines()]
if contents:
    with codecs.open(INDEX_FILE, 'w', 'utf8') as f:
        found_start = False
        for line in contents:
            if not found_start:
                f.write(line)
            if '<!-- BLOG_HEADLINES_START -->' in line:
                f.write(HTML)
                found_start = True
                continue
            if '<!-- BLOG_HEADLINES_END -->' in line:
                found_start = False
                f.write(line)
                continue
