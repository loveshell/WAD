import re
import os
from wad import tools
from wad.clues import _Clues
import itertools

CLUES_FILE = os.path.join(os.path.dirname(__file__), '../etc/apps.json')


def get_fields(app, key, rules_list):
    # returns a list of (app-ruletype-rule, fieldkey, fieldvalue) tuples,
    # e.g. ('LabVIEW-headers-Server', 'version', '\\1')
    return map(
        lambda (k, v): [("%s-%s-%s" % (app, key, k), k1, v1) for (k1, v1) in v.iteritems() if k1 != 're'],
        rules_list
    )


def test_clues_correct():
    #
    # If there's an error, run py.test with -l option to see which field has failed.
    #
    clues = _Clues()
    clues.load_clues(CLUES_FILE)
    apps, categories = clues.apps, clues.categories
    types = {}
    fields = {
        'implies': {'expected_type': list, 'min_expected_amount': 220},
        'excludes': {'expected_type': list, 'min_expected_amount': 5},
        'script': {'expected_type': list, 'min_expected_amount': 205},
        'url': {'expected_type': list, 'min_expected_amount': 33},
        'headers': {'expected_type': dict, 'min_expected_amount': 255},
        'html': {'expected_type': list, 'min_expected_amount': 230},
        'meta': {'expected_type': dict, 'min_expected_amount': 160},
        'env': {'expected_type': list, 'min_expected_amount': 225},
    }
    basic_fields = {
        'website': {'min_expected_amount': len(apps)},
        'cats': {'min_expected_amount': len(apps)},
        'catsStr': {'min_expected_amount': len(apps)},
    }
    expected_str_types = set([str, unicode])

    for app in apps:
        for t in apps[app]:
            tools.count(types, t)

    # check if all categories listed in app are defined
    assert set(reduce(list.__add__, [apps[a]['cats'] for a in apps])) <= set([int(x) for x in categories.keys()])

    # check if only expected fields are defined for apps
    assert set(types.keys()) == set(fields.keys() + basic_fields.keys())

    # check if numbers of entries are as expected
    assert len(apps) > 700
    for field, field_dict in itertools.chain(fields.iteritems(), basic_fields.iteritems()):
        assert types[field] >= field_dict['min_expected_amount']

    # check if all implies are lists of unicodes, headers and meta are dictionaries of str/unicode,
    # and others (including app names) are str/unicode
    assert set([type(a) for a in apps]) <= expected_str_types

    for field, field_dict in fields.iteritems():
        assert set([type(apps[a][field]) for a in apps if field in apps[a]]) <= set([field_dict['expected_type']])
        assert set([type(v) for a in apps if field in apps[a] for v in apps[a][field]]) <= expected_str_types

    for field in ['headers', 'meta']:
        assert set(
            [type(apps[a][field][k]) for a in apps if field in apps[a] for k in apps[a][field]]) <= expected_str_types

    # check if all 'implies' and 'excludes' references exist
    for field in ['implies', 'excludes']:
        assert set(reduce(list.__add__, [apps[a][field] for a in apps if field in apps[a]])) <= set(apps.keys())


def test_compile_clue():
    assert _Clues.compile_clue("abc") == {"re": re.compile("abc", flags=re.I)}
    assert _Clues.compile_clue("abc\;version:$1") == {"re": re.compile("abc", flags=re.I), "version": "$1"}
    assert _Clues.compile_clue("ab;c\;k:v1:v2\;aaa") == {"re": re.compile("ab;c", flags=re.I),
                                                         "k": "v1:v2", "aaa": None}


def test_compile_clues():
    clues = _Clues()
    clues.load_clues(CLUES_FILE)
    clues.compile_clues()
    apps = clues.apps

    # check optional fields like 'version' and 'confidence'
    fields = []
    for app in apps:
        for key in apps[app]:
            if key in ['script', 'html', 'url']:
                fields += reduce(list.__add__, get_fields(app, key, list(enumerate(apps[app][key + '_re']))))
            if key in ['meta', 'headers']:
                fields += reduce(list.__add__, get_fields(app, key, tools.dict2list(apps[app][key + '_re'])))

    assert len(fields) > 200
    # print(fields)

    # are there only 'version' and 'confidence' fields?
    assert set([k for (_, k, _) in fields]) == set(['confidence', 'version'])

    # are 'confidentiality' values always between 0 and 100?
    assert (filter(lambda x: not (0 < int(x) < 100), set([v for (_, k, v) in fields if k == 'confidence']))
            == [])

    # are 'version' values known/expected? or any new? if new, then test whether they work fine
    assert (set([v for (_, k, v) in fields if k == 'version']) ==
            set(['\\1 \\2', '\\1?Enterprise:Community', '\\1', '\\1?UA:', '\\1?4:5',
                 '\\1?4.1+:', '\\1.\\2.\\3', '\\1?2+:', 'API v\\1', '2+']))
