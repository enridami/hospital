import os
import sys 
sys.path.insert(0, os.path.abspath('../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'hospital.settings'
os.environ["secret_key"] = "fake_key_for_docs"
import django
django.setup()


project = 'Documentacion Hospital'
copyright = '2025, Gabriel, Raul, Enrique'
author = 'Gabriel, Raul, Enrique'
release = '1.0'


extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode', 'sphinx.ext.githubpages']

templates_path = ['_templates']
exclude_patterns = []

language = 'es'


html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
