# Module tools
#
# Author: Sebastian Lopienski <Sebastian.Lopienski@cern.ch>


# python 2.5+ -> hashlib; before -> md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import logging
import sys

import urllib2


# ===========================================================================================================
# From http://badpopcorn.com/blog/2006/03/16/map-filter-and-reduce-over-python-dictionaries/

# Uses the list composition to make the key value pairs over a dictionary.
dict2list = lambda dic: [(k, v) for (k, v) in dic.iteritems()]

# Use the built in dictionary constructor to convert the list.
list2dict = lambda lis: dict(lis)
# ===========================================================================================================


def count(d, e):
    # TODO: Use collections.Counter once moved to python 2.7
    if type(e) == list:
        for i in e:
            count(d, i)
    else:
        if e in d:
            d[e] += 1
        else:
            d[e] = 1


def hash_id(x):
    return md5("%s" % x).hexdigest()[:8]


def urlopen(url, timeout):
    headers = {'User-Agent': 'Mozilla/5.0 Firefox/33.0'}
    req = urllib2.Request(url, None, headers)
    try:
        page = urllib2.urlopen(req, timeout=timeout)
    except TypeError:
        page = urllib2.urlopen(req)
    return page


def error_to_str(e):
    return str(e).replace('\n', '\\n')


def add_log_options(parser):
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False,
                      help="be quiet")

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="be verbose")

    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
                      help="be more verbose")

    parser.add_option("--log", action="store", dest="log_file", metavar="FILE", default=None,
                      help="log to a file instead to standard output")


def use_log_options(options):
    log_format = '%(asctime)s (' + hash_id(options) + '):%(module)s:%(levelname)s %(message)s'

    date_format = '%Y/%m/%d-%H:%M:%S'
    log_level = logging.WARNING

    if options.verbose:
        log_level = logging.INFO
    if options.debug:
        log_level = logging.DEBUG
    if options.quiet:
        log_level = logging.ERROR

    if options.log_file:
        logging.basicConfig(filename=options.log_file, level=log_level, format=log_format, datefmt=date_format)
    else:
        logging.basicConfig(stream=sys.stdout, level=log_level, format=log_format, datefmt=date_format)
