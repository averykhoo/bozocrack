import argparse
import hashlib
from urllib import FancyURLopener, unquote_plus
import itertools
import re

hash_pattern = re.compile('[0-9a-f]{32}|[0-9A-F]{32}')
hash_cache = None
target = 'hashes.txt'


def internet_on():
    import urllib2

    try:
        response = urllib2.urlopen('http://74.125.228.100', timeout=1)
        return True
    except urllib2.URLError:
        return False


def open_rainbow(path='cache'):
    lines = set([tuple(line.strip('\n').split(':')) for line in open(path, 'r') if ':' in line])
    return sorted(lines)


def add_rainbow(dictionary='dictionary.txt', cache_path='cache'):
    for word in (line.strip('\n') for line in open(dictionary)):
        append_cache(md5(word), word, filename=cache_path)


def md5(text):
    return hashlib.md5(text).hexdigest()


def append_cache(hash_, plaintext, filename='cache'):
    with open(filename, 'a') as f:
        f.write('\n' + hash_ + ':' + plaintext)
    return hash_, plaintext


def google(hash_):
    if internet:
        def parse(html):
            for s in ["('", "'", '.', ':', '?']:
                html = html.replace(s, ' ')
            html += ''.join(char if char.lower() in 'abcdefghijklmnopqrstuvwxyz' else ' ' for char in html)
            return set(''.join(char if ord(char) < 128 else ' ' for char in html).split())

        class MyOpener(FancyURLopener):
            version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

        text = MyOpener().open("http://www.google.com/search?q={hash}".format(hash=hash_)).read()
        for word in parse(text):
            yield word
        urls = (unquote_plus(url.split('&amp')[0]) for url in re.findall('<a href="/url\?q=?\'?([^"\'>]*)', text))
        for url in urls:
            text = MyOpener().open(url).read()
            for word in parse(text):
                yield word


def search_dict(hash_, word_list):
    for word in word_list:
        if hash_ == md5(word):
            return append_cache(hash_, word)


def optimize_cache(filename='cache'):
    print 'optimizing cache...'
    with open(filename, 'r') as f:
        lines = list(set([tuple(line_.strip('\n').split(':')) for line_ in f.readlines() if ':' in line_]))
        lines = sorted([':'.join(line_) for line_ in lines if line_[0] == md5(line_[1])])
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))
    print 'cache optimized'
    return lines


def search_cache(hash_):
    global hash_cache
    if not hash_cache:
        hash_cache = open_rainbow()
    for hash_word in hash_cache:
        if hash_word[0] == hash_:
            return hash_word


def break_hash(hash_, dict_=None, chars='abcdefghijklmnopqrstuvwxyz', len_=4, search=True):
    hash_dict = itertools.chain([''], (line_.strip('\n') for line_ in open(dict_))) if dict_ else ['']
    if search:
        hash_word = search_cache(hash_)
        if hash_word:
            return hash_word
        hash_dict = itertools.chain(google(hash_), hash_dict)
    for i in xrange(len_):
        hash_dict = itertools.chain(hash_dict, (''.join(k) for k in itertools.product(*tuple([chars] * (i + 1)))))
    hash_word = search_dict(hash_, hash_dict)
    if hash_word:
        return hash_word


def read_eval_print_loop():
    print '\nMD5 REPL'
    while True:
        s = raw_input('input:  (blank to exit)\n>>> ')
        if not s:
            print 'blank hash:\n -> ' + md5('')
            print 'exiting repl...'
            break
        if hash_pattern.match(s):
            print 'unhash:'
            hash_inv = break_hash(s, len_=2)
            if hash_inv:
                print ' -> ' + hash_inv[1]
            else:
                print ' -> not found :('
        hash_ = md5(s)
        print 'hash:\n -> ' + append_cache(hash_, s)[0]
        print ''
    optimize_cache()


def break_hashes(file_, dict_=None, chars='abcdefghijklmnopqrstuvwxyz', len_=0, search=True):
    hash_list = [h.lower() for line in open(file_) if hash_pattern.match(line) for h in hash_pattern.findall(line)]
    for h in hash_list:
        tup = break_hash(h, dict_=dict_, chars=chars, len_=len_, search=search)
        yield ':'.join(tup) if tup else h + ': hash not found :('


# read_eval_print_loop()
# h = md5('CorrectHorseBatteryStaple')
# print search_dict(h, google(h))
# print break_hash(md5('Xmas'), search=False, dict_='words4.txt')
# print break_hash(md5('minecraft'))


if __name__ == "__main__":
    internet = internet_on()

    # define args
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='filein', help='input file (hash list)')
    parser.add_argument('-d', dest='dictionary', help='dictionary (word list)')
    parser.add_argument('-o', dest='fileout', help='output file (unhashed list)')
    parser.add_argument('-r', action='store_true', help='enable repl')


    # parse args
    args = parser.parse_args()
    f_in = args.filein
    f_out = args.fileout
    f_dict = args.dictionary
    repl_on = args.r

    if f_out and f_in:
        with open(f_out, 'w') as f:
            for result in break_hashes(f_in, dict_=f_dict):
                print result
                print >> f, result
        print 'saved to' + f_out
        optimize_cache()
    elif f_in:
        for result in break_hashes(f_in, dict_=f_dict):
            print result
        optimize_cache()
    elif target and not repl_on:
        print 'no args, using target defined in .py file'
        for result in break_hashes(target, len_=5):
            print result
        optimize_cache()
    else:
        print 'nothing to do'
        print parser.format_help()
    if repl_on:
        read_eval_print_loop()
    print 'done!'

