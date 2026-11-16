CIGA documentation
==================

This repository builds the `CIGA documentation <https://ciga-docs.readthedocs.io/>`_.
The current guide describes CIGA 0.1.6, available on PyPI.

The canonical guide is maintained in the ``docs/`` directory of the
`CIGA source branch <https://github.com/MediaCompLab/ciga/tree/codex/p5-temporal-access-20261102/docs>`_. This guide
corresponds to release source revision ``5286afa07a5b685f734d540a3422fe7334bf51a9``
and includes release-status updates. ``docs/requirements.txt`` pins the same
published version for Sphinx autodoc. When syncing a later release, update the
guide and package pin together and verify the build.

To build locally with Python 3.11 or later::

    python -m pip install -r docs/requirements.txt
    python -m sphinx -b html -W --keep-going docs/source build/html
