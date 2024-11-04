import os
from pathlib import Path

import configparser


def create():
    parser.add_section('language')
    parser.set('language', 'language', 'en')
    
    with open(config_path, 'w') as configfile:
        parser.write(configfile)

def set_up():
    theme = parser.get('language', 'language')
    
    return theme

def update(language):
    parser.set('language', 'language', language)
    
    with open(config_path, 'w') as configfile:
            parser.write(configfile)


parser = configparser.ConfigParser()

config_path = os.path.join(str(Path(__file__).parent), 'assets', 'conf.ini')

if not os.path.isfile(config_path):
    create()
else:
    parser.read(config_path)
