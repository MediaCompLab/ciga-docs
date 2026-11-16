CIGA documentation
==================

.. warning::

   This is a preview of the CIGA 0.1.6 development candidate. Version 0.1.6
   has not yet been published; these pages do not describe the current PyPI release.

CIGA analyzes character interactions over time using graphs and hypergraphs.
Graphs summarize pairwise relationships; hypergraphs preserve each group interaction
as an event, including repeated events and speaker/listener roles.

Start with :doc:`installation`, then run the self-contained :doc:`tutorials`.
These pages describe CIGA |release|, including graph and hypergraph support.

.. list-table:: Find the right guide
   :header-rows: 1
   :widths: 40 60

   * - I want to...
     - Read
   * - Prepare columns, time positions and weights
     - :doc:`data`
   * - Select graph snapshots or time windows
     - :doc:`graph`
   * - Keep group interactions as events
     - :doc:`hypergraph`
   * - Choose and interpret a graph metric
     - :doc:`analysis`
   * - Explore a network or export a figure/animation
     - :doc:`visualization`

.. toctree::
   :maxdepth: 2
   :caption: Guides and reference

   installation
   migration_0_1_6
   tutorials
   data
   graph
   signed_weights
   multilayer
   hypergraph
   analysis
   scientific_methods
   visualization
   Legal

For research citations, use the repository's ``CITATION.cff`` or GitHub's
**Cite this repository** entry. Development priorities and verification records
are in ``project-docs/IMPROVE_PLAN.md``; contributor setup is in ``CONTRIBUTING.md``.
