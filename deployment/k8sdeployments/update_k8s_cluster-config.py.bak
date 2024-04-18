import sys
from pathlib import Path

from ruamel.yaml import YAML

file_name = Path('k8s_cluster_config.yaml')
ip_address = sys.argv[1]

yaml = YAML()

with open("./k8s_cluster_config.yaml", "r") as stream:
    docs = list(yaml.load_all(stream))
    for num, doc in enumerate(docs, start=0):
        if num == 0:
            print ip_address
            doc['localAPIEndpoint']['advertiseAddress'] = ip_address
        else:
            # authorization = "{0}-{1}".format('authorization', 'mode')
            ext = {'authorization-mode': "{0},{1}".format('RBAC', 'Node'),
                   'oidc-client-id': 'ucpadvisor',
                   'oidc-issuer-url': 'https://keycloak:8081/auth/realms/ucpsystem',
                   'oidc-username-claim': 'preferred_username',
                   'oidc-groups-claim': 'groups',
                   'oidc-username-prefix': "-",
                   'oidc-groups-prefix': "groups:"}
            doc['apiServer'] = dict(extraArgs=ext)

with open("./k8s_cluster_config.yaml", "w") as stream:
    yaml.dump_all(
        docs,
        stream)
