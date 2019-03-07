import hashlib
from binascii import hexlify


def md5(text):
    return hexlify(hashlib.md5(text).digest())


def clean_file(path):
    with open(path, 'r') as f:
        lines = list(set([tuple(line.strip('\n').split(':')) for line in f.readlines() if ':' in line]))
        lines = sorted([':'.join(line) for line in lines if line[0] == md5(line[1])])
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':

    clean_file('cache')

    while True:
        s = raw_input('input:\n')
        if len(s) == 0:
            break
        h = md5(s)

        with open('cache', 'a') as f:
            f.write('\n' + h + ':' + s)
        print 'output:\n' + h + '\n'

    print 'done!'
