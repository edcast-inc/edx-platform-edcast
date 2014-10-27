from yaml import load
from yaml import YAMLObject, Loader, Dumper
import logging
import re
log = logging.getLogger(__name__)
CRED_FILE = '/edx/app/edxapp/meta_data.yml'

class ImmutableMash(YAMLObject):
    """
    Custom YAML object to handle loading of the Chef Immutable
    Mash type.
    """
    yaml_loader = Loader
    yaml_dumper = Dumper

    yaml_tag = u'!map:Chef::Node::ImmutableMash'

    @classmethod
    def from_yaml(cls, loader, node):
        return node.value


class ImmutableArray(YAMLObject):
    """
    Custom YAML object to handle loading of the Chef Immutable
    Array type.
    """
    yaml_loader = Loader
    yaml_dumper = Dumper

    yaml_tag = u'!seq:Chef::Node::ImmutableArray'

    @classmethod
    def from_yaml(cls, loader, node):
        return node.value

# Private methods to retrieve values from the yaml files based on the
# keys. Not to be exposed as API.
def _app_id():
    with open(CRED_FILE, 'r') as y:
        return load(y)[':app_id']

def _callback_url():
    with open(CRED_FILE, 'r') as y:
       return load(y)[':callback_url']

def _api_key():
    with open(CRED_FILE, 'r') as y:
        return load(y)[':credentials'][0].value[1][1].value

def _shared_secret():
    with open(CRED_FILE, 'r') as y:
        for x in y:
            if not re.match(".*shared_secret", x) == None:
                return x.split(":")[1].strip(" ")
        #log.info(str(load(y)[':credentials'][0]))
        #return load(y)[':credentials'][0].value[0][1].value

# permitted lookup values for the YAML file. These need to be updated
# along with any update in the YAML file.

KEYS = {
    'app_id': _app_id,
    'api_key': _api_key,
    'callback_url': _callback_url,
    'shared_secret': _shared_secret,
}


# Sole function exposed as the API from this module.
# allows lookup in the metadata file based on the incoming request.
# raises KeyError and fails silently by returning none for any
# illegal request.

# each call results in an IO. For multiple usage of cm_credentials(key), 
# it is preferred to assigns the value to a variable and use the variable
# as needed.
def cm_credentials(key):
    try:
        return KEYS[key]()
    except KeyError:
        return None
