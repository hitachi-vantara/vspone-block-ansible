import sys
from pathlib import Path

from ruamel.yaml import YAML

file_name = Path('keycloak-service.yaml')

ip_address = sys.argv[1]

yaml = YAML()
data = yaml.safe_load(file_name)
data['spec']['externalIPs'] = [ip_address]
yaml.dump(data, sys.stdout)
yaml.dump(data, Path('keycloak-service.yaml'))

# data['storage'][engine] = dict(engineConfig=dict(cacheSizeGB=size))
