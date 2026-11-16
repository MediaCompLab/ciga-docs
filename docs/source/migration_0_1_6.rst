Migrating from CIGA 0.1.5 to 0.1.6
===================================

This guide compares the published PyPI 0.1.6 and 0.1.5 packages. Check the exact package and
dependency versions in each research environment; the old development checkout
also advertised 0.1.5 despite containing code not present in the PyPI wheel.

Weighted centralities now require edge weights
----------------------------------------------

For graph degree, betweenness, closeness and harmonic centrality, a graph with
edges and no ``weight`` edge attribute now raises ``ValueError`` when
``weighted=True``. In 0.1.5 those weighted result columns could instead contain
zeros. The same rule applies to the corresponding temporal wrappers, including
snapshots returned by custom getters. An edgeless graph does not need a weight
attribute; unweighted analysis remains available. Individual edge weights must
also be finite real values; missing or NaN values are invalid.

``tgraph_diameter(..., weighted=True)`` now also raises for a nonempty snapshot
without weights instead of silently computing an unweighted diameter. The static
``graph_diameter`` already requires the requested weight attribute.

Choose the intended interpretation explicitly::

    import igraph as ig
    import ciga as cg

    graph = ig.Graph(n=3, edges=[(0, 1), (1, 2)])
    # If connections are unweighted, use the unweighted metric.
    unweighted = cg.graph_betweenness_centrality(graph, weighted=False)

    # Only if each edge really represents one unit of distance:
    graph.es['weight'] = [1.0] * graph.ecount()
    weighted = cg.graph_betweenness_centrality(graph, weighted=True)

Unit weights are a modelling choice, not a replacement for missing research data.
Shortest-path centralities interpret weights as strictly positive distances;
degree interprets them as strengths. A normal ``TGraph`` requires event weights
and constructs weighted snapshots. Existing TDA distance conversion has a
separate documented unit-distance convention when its attribute is absent; this
centrality change does not modify that convention.

Recheck previous results and ordering
-------------------------------------

The following independently checked results differ from the published 0.1.5 wheel:

* A cumulative query that moves before the first event and then forward no longer
  discards previously observed history.
* Editing already-consumed rows of the public ``TGraph.data`` is reflected in a
  subsequent cumulative query instead of reusing stale weights or endpoints.
* Certain large integer time coordinates compared against rounded floating bounds
  no longer include a future event. Hypergraph bounds also preserve their numeric
  comparison semantics.
* Raw closeness and harmonic centrality now use igraph's unnormalized distance
  calculations, matching their documented definitions. Normalized harmonic values
  are divided by the snapshot vertex count minus one exactly once. Previously,
  igraph's normalized defaults were reported as raw values and the normalized
  harmonic columns divided those values a second time. This affects static and
  temporal analyses; normalized closeness keeps its prior definition.
* On undirected graphs, passing ``directed=True`` to betweenness centrality no
  longer applies the directed normalization denominator. The option has no
  effect on an undirected graph, matching its documented contract.
* Graph persistence now projects directed edges symmetrically even when the weight
  attribute is absent, warning that direction is discarded. Parallel and opposite
  edges use the minimum converted distance rather than accumulating sparse entries;
  self-loops are omitted. Recompute affected persistence diagrams rather than
  comparing only matrix shape or graph vertex count.

Rerun affected analyses rather than treating the old outputs as an oracle. Graph
vertex order and temporal result-row order can also differ. Match vertices by name
and rows by time coordinates and character; do not assume positional vertex IDs
or row order stay fixed across versions. Graph snapshots now include the
``weight_policy`` attribute, and invalid normalization messages list the additional
signed-weight normalization methods. The recorded release comparison covers
selected workloads, not every function or dataset.

Memory states and temporal paths
--------------------------------

``accumulate_weights`` now defaults to ``ltm_rate=0``. To retain the former
additional undiscounted cumulative contribution, pass ``ltm_rate=1`` explicitly.
With ``time=``, the integer-converted time and position tuples must map one-to-one;
ambiguous mappings now raise rather than assigning events to the wrong position.
Its result adds a boolean ``_ciga_observed_event`` column recording whether a pair
actually interacted at each step; include it when retaining or exporting the table.
With this marker, temporal graph analyses and viewers default to memory snapshots,
and core temporal reachability uses only observed event rows. Raw event graphs still
default to cumulative analysis. Pass an explicit mode to override these defaults.
If provenance has been lost, provide the original event table via ``data=`` to the
core temporal reachability functions. See :doc:`data` for limitations.

New graph options and persistence
---------------------------------

``TGraph`` now supports opt-in signed weights and copied metadata. The default
``weight_policy='positive'`` rejects negative event weights; select ``'signed'``
only when signed interaction balances are the intended model. See
:doc:`signed_weights` for valid algorithms and transforms. ``TMultiLayerGraph``
can preserve raw named layers before projection; see :doc:`multilayer`.

A published 0.1.5 graph/hypergraph pickle fixture loads in the tested compatible
dependency environment, and derived graph caches are rebuilt. This is not a
guarantee for all pickles or dependency versions. Load pickle files only from
trusted sources. Older CIGA versions cannot load the new ``TMultiLayerGraph``
class: retain raw layers, initial graphs and metadata for reconstruction or
downgrade, and note that a CSV alone does not preserve all of that state.

Installation and reproducibility
--------------------------------

After publication, use ``python -m pip install "ciga==0.1.6"``. Before then,
install the exact reviewed source commit; simply installing ``ciga==0.1.5``
selects the published old package. See :doc:`installation` for extras.
Record the CIGA version or commit, Python and dependency versions, input-data
identity, analysis parameters and random seeds alongside research outputs.
Community IDs are snapshot-local and can change even when a partition is equivalent.
