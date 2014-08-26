#!/usr/bin/env python

import collections, json, os, textwrap

# This script generates the benchmark_config and setup_*.py files.
# To add new tests, modify the `configurations` and `test_urls` tables.

# Each line corresponds to a test application.
# Format is: (language, orm, (opsys, ...), (test, ...))
# See the dir_name logic below to see the directory name for each test application.
configurations = [
  ('Java',  None,    ['Linux'],            ['json']),
  ('Java',  'Ebean', ['Linux'],            ['db', 'query']),
  ('Scala', None,    ['Linux'],            ['json']),
  ('Scala', 'Anorm', ['Linux', 'Windows'], ['db', 'query', 'fortune', 'update']),
  ('Scala', 'Slick', ['Linux'],            ['db', 'query', 'fortune', 'update']),
]

# All play2 test applications must use the same URLs.
test_urls = {
  'json': '/json',
  'db': '/db',
  'query': '/queries?queries=',
  'fortune': '/fortunes',
  'update': '/update?queries=',
}

langs = {
  'Java': ['Java', 'play2-java'],
  'Scala': ['Scala', 'play2-scala']
}
def pathForLang(lang):
  return os.path.join(frameworksPath(), *langs[lang])
def frameworksPath():
  'Get the absolute path of ROOT/frameworks'
  return os.path.abspath(os.path.join(__file__, '..', '..', '..'))

lang_test_configs = {}
for lang, _ in langs.iteritems():
  lang_test_configs[lang] = collections.OrderedDict()

for lang, orm, opsyses, tests in configurations:
  dir_name = 'play2-' + lang.lower() + (('-'+orm.lower()) if orm else '')
  setup_name = 'setup_' + lang.lower() + (('_'+orm.lower()) if orm else '')

  setup_path = os.path.join(pathForLang(lang), setup_name+'.py')
  print 'Generating', setup_path
  with open(setup_path, 'w') as f:
    f.write(textwrap.dedent("""
      # This file was generated by frameworks/Java/play2-java/generate_config.py.
      # Do not edit this file directly, use the script to regenerate.
      from .setup_common import make_setup_for_dir

      make_setup_for_dir(globals(), '"""+dir_name+"""')
    """))

  for opsys in opsyses:
    if len(opsyses) == 1:
      test_name = lang.lower() + (('-'+orm.lower()) if orm else '')
    else:
      test_name = lang.lower() + (('-'+orm.lower()) if orm else '') + '-'+opsys.lower()
    test_config_json = collections.OrderedDict([
      ('display_name', 'play2-'+test_name),
      ('setup_file', setup_name),
      ('framework', 'play2'),
      ('language', lang),
      ('orm', orm if orm else 'Raw'),
      ('os', opsys),
      ('database', 'MySQL' if orm else 'None'),
      ('approach', 'Realistic'),
      ('classification', 'Fullstack'),
      ('platform', 'Netty'),
      ('webserver', 'None'),
      ('database_os', 'Linux'),
      ('notes', ''),
      ('versus', 'netty'),
      ('port', '9000'),
    ])
    for test in tests:
      test_config_json[test+'_url'] = test_urls[test]
      lang_test_configs[lang][test_name] = test_config_json

for lang, _ in langs.iteritems():
  benchmark_config_path = os.path.join(pathForLang(lang), 'benchmark_config')
  print 'Generating', benchmark_config_path
  with open(benchmark_config_path, 'w') as f:
    json_str = json.dumps({
      'framework': 'play2',
      'tests': [lang_test_configs[lang]]
    }, indent=2)
    f.write(json_str)