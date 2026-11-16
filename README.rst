CIGA documentation preview
==========================

This repository builds the Read the Docs site. The documentation on this branch
describes the CIGA 0.1.6 development candidate, which has not yet been released.
Do not merge it into the published documentation branch until the corresponding
package release is ready.

The canonical guide is maintained in the ``docs/`` directory of the
`CIGA source repository <https://github.com/MediaCompLab/ciga>`_. This snapshot
comes from commit ``5286afa07a5b685f734d540a3422fe7334bf51a9``. The package
dependency in ``docs/requirements.txt`` is pinned to that same commit, so Sphinx
autodoc cannot silently document an older PyPI release. When syncing later,
update the guide and package pin together, verify the build, and remove the
development notices when 0.1.6 is actually released.

To build locally with Git and Python 3.11 or later::

    python -m pip install -r docs/requirements.txt
    python -m sphinx -b html -W --keep-going docs/source build/html

The published documentation is at https://ciga-docs.readthedocs.io/.
