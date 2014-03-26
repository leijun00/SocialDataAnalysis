# -*- coding: utf-8 -*-
import os
import json
import webbrowser
import weibo
import jieba
import jieba.posseg

MIN_FREQUENCY = 2
HTML_TEMPLATE = os.path.join(os.getcwd(),'tagcloud_template.html')
MIN_FONT_SIZE = 5
MAX_FONT_SIZE = 20
# input your own access token here
ACCESS_TOKEN = ''
UIDS=[1813340115]

def get_timeline(url, access_token, uid, since_id=0, max_id=0, count=200, page=1, trim_user=1):
    while 1:
        ret = weibo._http_get(url, authorization=access_token, uid=uid, since_id=since_id, max_id=max_id, count=count, page=page, trim_user=trim_user)
        if ret.has_key('statuses') is False or len(ret['statuses']) == 0:
            return

        for tweet in ret['statuses']:
            if tweet['id'] >= since_id:
                if max_id == 0:
                    max_id = tweet['id']
                yield tweet

        page += 1

def get_tag(url, access_token, uid, count=20, page=1, trim_user=1):
    while 1:
        ret = weibo._http_get(url, authorization=access_token, uid=uid, count=count, page=page)
        if len(ret) < 5:
            return
        for dict in ret:
            yield dict

        page += 1

def weightTermByFreq(f):
        return (f - min_freq) * (MAX_FONT_SIZE - MIN_FONT_SIZE) / (max_freq - min_freq) + MIN_FONT_SIZE

jieba.initialize()
for UID in UIDS:
    print 'processing for %s' % UID
    word_dict = {}
    tweets = get_timeline(r'https://api.weibo.com/2/statuses/user_timeline.json', ACCESS_TOKEN, UID)
    if tweets is not None:
        for tweet in tweets:
            wlist = jieba.posseg.cut(tweet['text'])
            for wf in wlist:
                if wf.flag != 'n':
                    continue
                w = wf.word
                if word_dict.has_key(w):
                    word_dict[w] = word_dict[w]+1
                else:
                    word_dict[w] = 1

    ret = get_tag(r'https://api.weibo.com/2/tags.json', ACCESS_TOKEN, UID)
    if ret is not None:
        for dict in ret:
            for key in dict.keys():
                if key != 'weight':
                    word_dict[dict[key]] = 20

    for key in word_dict.keys():
        if len(key) == 1:
            word_dict.pop(key)

    raw_output = sorted([(term, '', freq) for (term, freq) in word_dict.iteritems() if freq >= MIN_FREQUENCY], key=lambda x: x[2])

    min_freq = raw_output[0][2]
    max_freq = raw_output[-1][2] if raw_output[-1][2] > min_freq else min_freq + 1

    weighted_output = [[i[0], i[1], weightTermByFreq(i[2])] for i in raw_output[-30:]]

    # substitute the JSON data structure into the template
    html_page = open(HTML_TEMPLATE).read() % (json.dumps(weighted_output),)

    output_file = os.path.join(os.getcwd(), str(UID)+'.html')
    f = open(output_file, 'w')
    f.write(html_page)
    f.close()

    webbrowser.open_new_tab(output_file)
    
    word_dict.clear()
    print 'processing for %s finished' % UID

print 'finished.'
