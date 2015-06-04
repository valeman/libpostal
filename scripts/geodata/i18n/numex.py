import os
import sys

import ujson as json

this_dir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(os.path.join(os.pardir, os.pardir)))

from geodata.encoding import safe_encode
from unicode_paths import DATA_DIR


NUMEX_DATA_DIR = os.path.join(DATA_DIR, 'numex', 'rules')

NUMEX_RULES_FILE = os.path.join(os.pardir, os.pardir, os.pardir, 'src', 'numex_data.c')

GENDER_MASCULINE = 'GENDER_MASCULINE'
GENDER_FEMININE = 'GENDER_FEMININE'
GENDER_NEUTER = 'GENDER_NEUTER'
GENDER_NONE = 'GENDER_NONE'

gender_map = {
    'm': GENDER_MASCULINE,
    'f': GENDER_FEMININE,
    'n': GENDER_NEUTER,
    None: GENDER_NONE,
}


CATEGORY_PLURAL = 'CATEGORY_PLURAL'
CATEGORY_DEFAULT = 'CATEGORY_DEFAULT'

category_map = {
    'plural': CATEGORY_PLURAL,
    None: CATEGORY_DEFAULT
}

LEFT_CONTEXT_MULTIPLY = 'NUMEX_LEFT_CONTEXT_MULTIPLY'
LEFT_CONTEXT_ADD = 'NUMEX_LEFT_CONTEXT_ADD'
LEFT_CONTEXT_NONE = 'NUMEX_LEFT_CONTEXT_NONE'

left_context_map = {
    'add': LEFT_CONTEXT_ADD,
    'multiply': LEFT_CONTEXT_MULTIPLY,
    None: LEFT_CONTEXT_NONE,
}

RIGHT_CONTEXT_MULTIPLY = 'NUMEX_RIGHT_CONTEXT_MULTIPLY'
RIGHT_CONTEXT_ADD = 'NUMEX_RIGHT_CONTEXT_ADD'
RIGHT_CONTEXT_NONE = 'NUMEX_RIGHT_CONTEXT_NONE'

right_context_map = {
    'add': RIGHT_CONTEXT_ADD,
    'multiply': RIGHT_CONTEXT_MULTIPLY,
    None: RIGHT_CONTEXT_NONE,
}

CARDINAL = 'NUMEX_CARDINAL_RULE'
ORDINAL = 'NUMEX_ORDINAL_RULE'

rule_type_map = {
    'cardinal': CARDINAL,
    'ordinal': ORDINAL
}

numex_rule_template = u'{{"{key}", (numex_rule_t){{{left_context_type}, {right_context_type}, {rule_type}, {gender}, {category}, {radix}, {value}LL}}}}'

stopword_rule_template = u'{{"{key}", NUMEX_STOPWORD_RULE}}'

ordinal_indicator_template = u'{{"{key}", {gender}, {category}, "{value}"}}'

stopwords_template = u'"{word}"'

language_template = u'{{"{language}", {rule_index}, {num_rules}, {ordinal_indicator_index}, {num_ordinal_indicators}}}'

numex_rules_data_template = u'''
numex_rule_source_t numex_rules[] = {{
    {numex_rules}
}};

ordinal_indicator_t ordinal_indicator_rules[] = {{
    {ordinal_indicator_rules}
}};

numex_language_source_t numex_languages[] = {{
    {languages}
}};
'''


def parse_numex_rules(dirname=NUMEX_DATA_DIR, outfile=NUMEX_RULES_FILE):
    all_rules = []
    all_ordinal_indicators = []
    all_stopwords = []

    all_languages = []

    out = open(outfile, 'w')

    for filename in os.listdir(dirname):
        path = os.path.join(dirname, filename)
        if not os.path.isfile(path) or not filename.endswith('.json'):
            continue

        language = filename.split('.json', 1)[0]

        data = json.load(open(path))

        rules = data.get('rules', [])
        rule_index = len(all_rules)

        for rule in rules:
            gender = gender_map[rule.get('gender')]
            rule_type = rule_type_map[rule['type']]
            key = rule['name']
            value = rule['value']
            radix = rule.get('radix', 10)
            category = category_map[rule.get('category')]
            left_context_type = left_context_map[rule.get('left')]
            right_context_type = right_context_map[rule.get('right')]
            all_rules.append(unicode(numex_rule_template.format(
                key=key,
                language=language,
                rule_type=rule_type,
                gender=gender,
                category=category,
                left_context_type=left_context_type,
                right_context_type=right_context_type,
                value=value,
                radix=radix
            )))

        ordinal_indicator_index = len(all_ordinal_indicators)
        ordinal_indicators = data.get('ordinal_indicators', [])
        num_ordinal_indicators = 0

        for rule in ordinal_indicators:
            gender = gender_map[rule.get('gender')]
            category = category_map[rule.get('category')]
            if 'suffixes' not in rule:
                print rule.keys()

            for key, suffixes in rule['suffixes'].iteritems():
                for suffix in suffixes:
                    all_ordinal_indicators.append(unicode(ordinal_indicator_template.format(
                        key=key,
                        value=suffix,
                        gender=gender,
                        category=category
                    )))
                num_ordinal_indicators += len(suffixes)

        stopwords = data.get('stopwords', [])
        stopword_index = len(all_stopwords)
        num_stopwords = len(stopwords)

        for stopword in stopwords:
            all_rules.append(unicode(stopword_rule_template.format(key=stopword)))

        num_rules = len(rules) + len(stopwords)

        all_languages.append(unicode(language_template.format(
            language=language,
            rule_index=rule_index,
            num_rules=num_rules,
            ordinal_indicator_index=ordinal_indicator_index,
            num_ordinal_indicators=num_ordinal_indicators
        )))

    out.write(safe_encode(numex_rules_data_template.format(
        numex_rules=u''',
    '''.join(all_rules),
        ordinal_indicator_rules=u''',
    '''.join(all_ordinal_indicators),
        stopwords=u''',
    '''.join(all_stopwords),
        languages=u''',
    '''.join(all_languages),
    )))

    out.close()


if __name__ == '__main__':
    parse_numex_rules(*sys.argv[1:])
