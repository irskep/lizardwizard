import urllib
import urllib2
import json
import re
import HTMLParser
import formatter

def strip_ml_tags(in_text):
    """Description: Removes all HTML/XML-like tags from the input text.
    Inputs: s --> string of text
    Outputs: text string without the tags
    
    # doctest unit testing framework
    
    >>> test_text = "Keep this Text <remove><me /> KEEP </remove> 123"
    >>> strip_ml_tags(test_text)
    'Keep this Text  KEEP  123'
    """
    # convert in_text to a mutable object (e.g. list)
    s_list = list(in_text)
    i,j = 0,0
    
    while i < len(s_list):
        # iterate until a left-angle bracket is found
        if s_list[i] == '<':
            while s_list[i] != '>':
                # pop everything from the the left-angle bracket until the right-angle bracket
                s_list.pop(i)
                
            # pops the right-angle bracket, too
            s_list.pop(i)
        else:
            i=i+1
    
    # convert the list back into text
    join_char=''
    return join_char.join(s_list)

def unescape(s):
    p = HTMLParser.HTMLParser()
    return p.unescape(s)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

random_url = "http://en.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=%d"
info_url = "http://en.wikipedia.org/w/api.php?action=query&pageids=%s&format=json&prop=info&inprop=url"
mobile_url = "http://mobile.wikipedia.org/transcode.php?go=%s"

def req(url):
    return urllib2.urlopen(urllib2.Request(url, headers={'User-Agent': "LizardWizard/1.0"}))

def random_articles(n=1):
    return [i['id'] for i in json.load(req(random_url % n))['query']['random']]

def infos_for(pageids):
    j = json.load(req(info_url % '|'.join(str(i) for i in pageids)))['query']['pages'].itervalues()
    infos = {}
    for i in j:
        # print mobile_url % urllib.quote(i['title'])
        infos[i['title']] = mobile_url % urllib.quote(i['title'])
    return infos

def text_for(infos):
    texts = {}
    for title in infos.iterkeys():
        request = req(infos[title])
        encoding=request.headers['content-type'].split('charset=')[-1]
        texts[title] = unicode(request.read(), 'utf-8')
    return texts

single_tag_lines = re.compile(r'\n<[^>]+>\n')
html = re.compile(r'<.*?>')
list_fix = re.compile(r'\n-\n')
# brackets = re.compile(r'\[(?P<contents>[^\]]+)\]|{{(?P<contents>[^}]+)}}')
brackets = re.compile(r'\[|\]|{|}')

def sanitize(t):
    t = unescape(t)
    if 'Continue ...' in t:
        t = ''.join(t.split('<hr />')[1:-2])
    else:
        t = ''.join(t.split('<hr />')[1:-1])
    
    last_len = len(t) + 1
    while len(t) < last_len:
        last_len = len(t)
        t = single_tag_lines.sub('\n', t)
    
    t = strip_ml_tags(t)
    # t = list_fix.sub('\n-', t)
    t = brackets.sub('', t)
    
    lines = t.split('\n')
    new_lines = ['']
    
    def can_extend(l):
        if l.endswith('\n'):
            return False
        if len(l) < 120:
            return True
        return False
    
    for line in lines:
        if line:
            if line.strip().lower() in ('external links', 'references', 'see also'):
                break
            new_lines[-1] += line
        elif new_lines and new_lines[-1]:
            if len(new_lines[-1]) >= 120 or new_lines[-1].endswith('\n'):
                new_lines.append('')
            else:
                new_lines[-1] += '\n'
    while new_lines and not new_lines[-1]:
        new_lines = new_lines[:-1]
    return new_lines

def random_texts(n=1):
    errcount = 0
    while True:
        try:
            articles = random_articles(n)
            infos = infos_for(articles)
            texts = text_for(infos)
            for title in texts.iterkeys():
                texts[title] = sanitize(texts[title])
            return texts
        except urllib2.HTTPError as e:
            print e
            errcount += 1
        except KeyError:
            pass
        if errcount > 4:
            import sys
            sys.exit(1)

def vet_texts(texts):
    ok_texts = {}
    for t in texts.iterkeys():
        if 3 <= len(texts[t]):
            ok_texts[t] = texts[t]
    return ok_texts

def text_dicts(n=5):
    texts = {}
    retry=0
    while len(texts) < n:
        retry+=1
        if retry>1:
            print 'finding more appropriately sized articles...'
        texts.update(vet_texts(random_texts(n-len(texts))))
    return texts

if __name__ == '__main__':
    for k, v in text_dicts(1).iteritems():
        print k
        for line in v:
            print
            print line
