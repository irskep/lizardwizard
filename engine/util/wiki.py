import urllib2
import json
import re

random_url = "http://en.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=%d"
info_url = "http://en.wikipedia.org/w/api.php?action=query&pageids=%s&format=json&prop=info&inprop=url"

remove_crap = re.compile(r"{{[^}]+}}|\[\[\w:[^\]]+]")
remove_html = re.compile(r'<.*?>|\'\'\'?|\w+\.png\s*')
remove_doublebreaks = re.compile(r"\n\n\n+")
remove_sidebar = re.compile(r"\n(\||!|({\|))[^\n]*\n|\n}}\n")
remove_empties = re.compile(r"\(\)")
def req(url):
    return urllib2.urlopen(urllib2.Request(url, headers={'User-Agent': "LizardWizard/1.0"}))

def random_articles(n=1):
    return [i['id'] for i in json.load(req(random_url % n))['query']['random']]

def infos_for(pageids):
    j = json.load(req(info_url % '|'.join(str(i) for i in pageids)))['query']['pages'].values()
    
    return dict[(i['title'], i['fullurl'] + "?action=raw") for i in j]

def text_for(infos):
    texts = {}
    for title in infos.keys():
        texts[title] = req(url).read()
    return texts

def remove_useless_info(t):
    final_list = []

    for item in t.split('[['):
        s = item.split(']]')
        if len(s) == 2:
            left, right = item.split(']]')
            x = left.split('|')[0].split(':')[-1]
            final_list.append(x)
            final_list.append(right)
        else:
            final_list.append(s[0])
    return ''.join(final_list)

def truncate_footers(t):
    for stripper in ('References', 'See Also', 'External Links', 'Further Reading', 'External links', 'See also', 'Further reading', 'Media'):
        t = t.split('\n==%s==' % stripper)[0]
        t = t.split('\n== %s ==' % stripper)[0]
        t = t.split('\n== %s==' % stripper)[0]
        t = t.split('\n==%s ==' % stripper)[0]
    return t

def sanitize(t):
    t = remove_crap.sub('\n', t)
    t = remove_doublebreaks.sub('\n\n', t)
    t = remove_html.sub('', t)
    t = remove_sidebar.sub('\n', t)
    t = remove_sidebar.sub('\n', t)
    t = remove_sidebar.sub('\n', t)
    t = remove_useless_info(t)
    t = truncate_footers(t)
    t = remove_empties.sub('', t)
    while t[0] == '\n':
        t = t[1:]
    return t

def random_texts(n=1):
    infos = infos_for(random_articles(n))):
    for title in infos.keys():
        infos[title] = sanitize(infos[title])

# def worker():
#     while True:
#         item = q.get()
#         do_work(item)
#         q.task_done()
# 
# q = Queue()
# for i in range(num_worker_threads):
#      t = Thread(target=worker)
#      t.daemon = True
#      t.start()
# 
# for item in source():
#     q.put(item)
# 
# q.join()