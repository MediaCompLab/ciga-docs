Installation
============

CIGA 0.1.6 requires Python 3.9 or later. It includes graph/hypergraph data
structures, basic analysis and HTML visualization. Optional XGI/Hypergraphx backends
require Python 3.10 or later; Reticula requires Python 3.12 or later.

Published package
-----------------

After CIGA 0.1.6 is published, install this version from PyPI::

    python -m pip install "ciga==0.1.6"

Graph and hypergraph APIs are included in the same release. Before publication,
use the source checkout below.

Current source
--------------

From a terminal, clone and install CIGA in your active Python environment::

    git clone https://github.com/MediaCompLab/ciga.git
    cd ciga
    git checkout 5286afa07a5b685f734d540a3422fe7334bf51a9
    python -m pip install -e .

If you already have the checkout, run only the install command from its root.
Verify which copy Python loads::

    python -c "import ciga; print(ciga.__version__); print(ciga.__file__)"

Continue with :doc:`tutorials`.

Optional features
-----------------

The commands below target the PyPI release. From a checkout, replace
``"ciga[extra]==0.1.6"`` with ``-e ".[extra]"``.

.. list-table:: Extras
   :header-rows: 1
   :widths: 35 65

   * - Feature
     - Command
   * - GIF and MP4 export
     - ``python -m pip install "ciga[visualization]==0.1.6"``
   * - Persistent homology / TDA
     - ``python -m pip install "ciga[tda]==0.1.6"``
   * - Listener inference client
     - ``python -m pip install "ciga[llm]==0.1.6"``
   * - All three extras above
     - ``python -m pip install "ciga[all]==0.1.6"``
   * - All native hypergraph integrations
     - ``python -m pip install "ciga[hypergraph]==0.1.6"``
   * - Reticula only
     - ``python -m pip install "ciga[hypergraph-reticula]==0.1.6"``
   * - XGI only
     - ``python -m pip install "ciga[hypergraph-xgi]==0.1.6"``
   * - Hypergraphx only
     - ``python -m pip install "ciga[hypergraph-hgx]==0.1.6"``

``all`` does not include native hypergraph libraries. To combine both sets on
Python 3.12+, use ``python -m pip install "ciga[all,hypergraph]==0.1.6"``.
On Python 3.10/3.11, use ``ciga[hypergraph-xgi,hypergraph-hgx]==0.1.6`` for XGI/HGX.
Reticula 0.13's published metadata incorrectly permits older Python versions;
CIGA checks the actual requirement before importing that backend.
The ``visualization`` extra is for animation export; HTML graph and hypergraph
viewers work with the core installation.

pathpyG integration
-------------------

Only the pathpyG adapter and temporal betweenness wrapper need these additional
packages::

    python -m pip install torch
    python -m pip install git+https://github.com/pathpy/pathpyG.git

CIGA's ``temporal_reachability`` and ``earliest_arrival_times`` run without them.
See :doc:`analysis` for the distinction between snapshot metrics and time-respecting paths.
