import sys
import ruamel.yaml

yaml = ruamel.yaml.YAML()

with open('../demo_custom.yml') as fp:
    data = yaml.load(fp)

data['days_between_notifications'] = 40
data['strategy_db'][0]['name'] = 'Test'

with open('../demo_custom_1.yml', 'w') as ofp:
    yaml.dump(data, ofp)