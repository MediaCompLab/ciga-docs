Graph analysis
==============

Use ``graph_*`` functions for one ``igraph.Graph`` and ``tgraph_*`` functions for
results over time. Hypergraph metrics have separate definitions in :doc:`hypergraph`
and :doc:`hypergraph_backends`.
For formulas and a reproducible reporting example, see :doc:`scientific_methods`.

.. contents:: On this page
   :local:
   :depth: 2

Choose a measure
----------------

.. list-table:: Common questions
   :header-rows: 1
   :widths: 45 55

   * - Question
     - Function family
   * - How many connections, or how much interaction weight, does each actor have?
     - ``*_degree_centrality``
   * - Which actors lie on shortest paths?
     - ``*_betweenness_centrality``
   * - How close is an actor to the others?
     - ``*_closeness_centrality`` or ``*_harmonic_centrality``
   * - How do connections to other highly scored actors affect a score?
     - ``*_eigenvector_centrality``; select the fallback policy below.
   * - Which actors form communities?
     - ``*_community_leiden``, ``*_community_multilevel`` or ``*_community_label_propagation``
   * - How does the whole network change?
     - Density, connectivity, diameter, reciprocity or TDA functions.
   * - Can a path follow the order of observed interactions?
     - Temporal reachability functions; cumulative graph paths do not enforce time order.

Read the result table
---------------------

Static centralities return a DataFrame in ``g.vs`` order; add names with
``result.insert(0, 'character', g.vs['name'])``. Temporal centralities return time
columns, ``character`` and metrics. Community tables include ``character`` and
``community``. Graph properties return a scalar for one graph, or one row per
reported time step for temporal analysis.

Continue with ``tg`` from :doc:`tutorials`::

    degree = cg.tgraph_degree_centrality(tg, accumulate=False, weighted=True)
    density = cg.tgraph_density(tg, accumulate=False)

Temporal graph analysis defaults to cumulative history for raw interactions and
snapshots for marked memory states. ``accumulate=False`` selects snapshots explicitly;
``accumulate=True`` selects cumulative history; ``window_size`` overrides accumulation
and counts observed steps.
Use ``start``, ``end`` and ``stride`` to select reported steps (:doc:`graph`).

Weights and metric choices
--------------------------

``cg.analysis_capabilities()`` lists the supported weight domains for covered
snapshot analyses. ``cg.get_analysis_capability(name, weighted=True)`` describes a
weighted configuration, independently of the actual function's default. For
Leiden, also supply ``objective_function``. The registry shares rules with input
guards; it does not certify backend availability or convergence. See :doc:`multilayer`
for query examples, signed projections and boundaries.

``weighted=True`` uses edge weights. Degree and eigenvector interpret them as
strengths; shortest-path metrics interpret them as distances. If your weights
are interaction strengths and reciprocal distance is your intended model, request
inversion explicitly::

    paths = cg.tgraph_betweenness_centrality(tg, weighted=True, invert_weight=True)

For degree, betweenness, closeness and harmonic centrality and temporal diameter, a graph with edges
must have a ``weight`` edge attribute when ``weighted=True``; missing weights
raise ``ValueError``. With ``weighted=False`` the attribute is not required.
Edgeless graphs need no weights. This also applies to graph snapshots supplied
by custom temporal getters. See :doc:`migration_0_1_6` for examples and other
changes from 0.1.5.

``w_normalized`` transforms input weights; ``normalized=True`` changes the
metric's output scale. These options are not interchangeable. Degree normalization
divides by n-1 when n > 1, including a two-vertex graph. Empty and single-vertex
graphs have zero normalized scores. Graph and hypergraph dyads use the same divisor.

For closeness, the raw score is the reciprocal of the sum of finite shortest-path
distances to or from other reachable vertices. Its normalized column multiplies
that score by the number of reachable other vertices, following igraph. For harmonic
centrality, the raw score is the sum of reciprocal finite distances; the normalized
column divides it by the full snapshot vertex count minus one. Unreachable vertices
contribute zero to harmonic centrality. Direction and ``cutoff`` determine which
paths are included. In a graph with edges, closeness may be NaN when a vertex cannot
reach any other vertex; edgeless graphs use zero by CIGA convention. See the
`igraph centrality reference <https://python.igraph.org/en/1.0.0/api/igraph.GraphBase.html>`_
for backend definitions.

For an undirected community model, construct undirected data explicitly. Using
``pairs`` and ``positions`` from :doc:`tutorials`::

    undirected = cg.TGraph(data=pairs, positions=positions, directed=False)
    communities = cg.tgraph_community_leiden(undirected, seed=42)

API reference
-------------

.. currentmodule:: ciga

Centrality Analysis
~~~~~~~~~~~~~~~~~~~

Eigenvector results include a ``centrality_method`` column. Set ``pagerank=False`` to
require eigenvector centrality and propagate solver errors. The legacy ``pagerank=True``
default allows warned PageRank fallbacks, identified as ``'pagerank'`` in that column;
the historical ``eigenvector_centrality`` score column is retained. Edgeless snapshots
have zero scores by convention and are marked ``'undefined'``. Select metric columns
explicitly when passing a result table to numerical code.

Static Graph Centrality
^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: graph_degree_centrality
.. autofunction:: graph_signed_strength
.. autofunction:: graph_betweenness_centrality
.. autofunction:: graph_closeness_centrality
.. autofunction:: graph_harmonic_centrality
.. autofunction:: graph_eigenvector_centrality

Temporal Graph Centrality
^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tgraph_degree_centrality
.. autofunction:: tgraph_signed_strength
.. autofunction:: tgraph_betweenness_centrality
.. autofunction:: tgraph_closeness_centrality
.. autofunction:: tgraph_harmonic_centrality
.. autofunction:: tgraph_eigenvector_centrality

Community Detection
~~~~~~~~~~~~~~~~~~~
.. autofunction:: graph_community_leiden
.. autofunction:: tgraph_community_leiden
.. autofunction:: graph_community_multilevel
.. autofunction:: tgraph_community_multilevel
.. autofunction:: graph_community_label_propagation
.. autofunction:: tgraph_community_label_propagation

.. note::

   Pass ``seed=`` for repeatable runs with the same data and dependency versions.
   Record the algorithm, parameters and versions alongside it. Community labels in
   separate temporal snapshots are not persistent identities.

Graph Properties
~~~~~~~~~~~~~~~~
.. autofunction:: graph_density
.. autofunction:: graph_transitivity_undirected
.. autofunction:: tgraph_density
.. autofunction:: tgraph_transitivity_undirected
.. autofunction:: graph_is_connected
.. autofunction:: tgraph_is_connected
.. autofunction:: graph_diameter
.. autofunction:: tgraph_diameter
.. autofunction:: graph_reciprocity
.. autofunction:: tgraph_reciprocity

Topological Data Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

Persistent homology over the interaction graph. Requires the ``tda`` extra
(``pip install ciga[tda]``).

The sparse matrix is built from direct edge distances, not all-pairs shortest
paths. A missing off-diagonal entry represents no finite edge. Directed edges
are treated as undirected with a warning; parallel or opposite edges use the
smallest converted distance for their vertex pair, and self-loops are omitted.
Unweighted edges have unit distance. Conversions apply to individual weighted
edges before selecting the minimum; ``max_minus`` uses the maximum supplied
edge weight. Explicit zero distances remain stored sparse entries. This
projection discards direction and is not a directed persistence method.
.. autofunction:: graph_persistence_diagram
.. autofunction:: tgraph_persistence_diagrams
.. autofunction:: tgraph_stability
.. autofunction:: graph_to_sparse_distance_matrix

Temporal Reachability Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reachability depends on event-time rules; it does not establish observed influence.
The core functions below need no extras and process full time-coordinate batches
in chronological order. Their ``strict`` option defines simultaneous transmission:

- ``strict=False`` (default): paths may use several edges at the same time.
  Every reachable path within a simultaneous batch is included.
- ``strict=True``: each successive edge must occur later. A newly reached actor
  can transmit only in a later batch, as with Reticula's strict time-order rule.

Both rules are independent of row order, for reachability sets, earliest arrival
times and the reachability sequence. If event order within a scene matters, include
the line/event position in ``positions`` instead of relying on CSV row order::

    simultaneous = pd.DataFrame({
        'time': [1, 1], 'source': ['B', 'A'], 'target': ['C', 'B'], 'weight': [1, 1],
    })
    ties = cg.TGraph(data=simultaneous, positions=('time',))
    assert cg.temporal_reachability(ties, 'A') == {'A', 'B', 'C'}
    assert cg.temporal_reachability(ties, 'A', strict=True) == {'A', 'B'}

The source is available before the first selected event. Earliest-arrival results
omit the source and unreachable actors. Weights do not affect transmission; even
observed zero-weight rows remain events. For memory states produced by
``accumulate_weights``, the ``_ciga_observed_event`` column identifies real
interactions; generated state-only rows do not transmit. Keep this column when
exporting or processing the states. If it has been removed or transformed, provide
the original events using ``data=`` to the core reachability functions instead.
The optional pathpyG adapter requires a graph built from raw interactions because
state weights cannot reconstruct original event weights.
``temporal_reachability_sequence`` defaults to
snapshots (``accumulate=False``) and ``normalize=True``; its denominator is the full
event/initial-vertex population minus one, independent of earlier graph queries.
Cumulative all-source reachability can require quadratic space in the vertex count.
.. autofunction:: temporal_reachability
.. autofunction:: earliest_arrival_times
.. autofunction:: temporal_reachability_sequence

The following wrap `pathpyG <https://github.com/pathpy/pathpyG>`_ and additionally require
``torch`` and ``pathpyG``; ``ciga.analysis.tra.PATHPYG_AVAILABLE`` reports whether they can
run in the current environment.
.. autofunction:: temporal_betweenness_centrality
.. autofunction:: get_pathpyg_temporal_graph
