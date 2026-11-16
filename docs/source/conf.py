"""Sphinx configuration for the standalone CIGA documentation repository."""

import ciga

project = 'CIGA'
copyright = '2025, Shu Hu'
author = 'Shu Hu'
release = ciga.__version__
version = ciga.__version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
