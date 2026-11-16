Scientific definitions and reproducibility
==========================================

These definitions describe CIGA's core snapshot metrics. The temporal wrappers
first choose a graph snapshot, cumulative history, or observed-step window, then
apply the same metric. They are not a full validation of every backend or dataset.
For native hypergraph centralities, communities and temporal reachability, see
:doc:`hypergraph_backends` for the method, backend and domain restrictions.

Pairwise graph metrics
----------------------

Let ``n`` be the number of vertices in the selected graph, and ``d(u,v)`` its
shortest-path distance under the selected direction and optional cutoff.

* Degree counts incident edges; strength sums their weights. Directed results
  distinguish incoming, outgoing and all edges. igraph counts an undirected loop
  twice, and a directed loop once in each of in and out. The optional normalized
  columns divide by ``n-1`` for ``n>1``, otherwise they are zero. Parallel edges
  and loops can make a normalized value exceed one.
* Betweenness sums, over eligible vertex pairs, the fraction of shortest paths
  between the pair that contain the vertex. The standard normalized denominator
  is ``(n-1)(n-2)`` for directed paths and half that for undirected paths;
  ``n<=2`` yields zero normalized scores. Source/target restrictions and a cutoff
  restrict considered paths, but the denominator remains based on full ``n``.
* Raw closeness is ``1 / sum(d(v,u))`` over reachable other vertices, and its
  normalized column multiplies by the count of those vertices. If no other vertex
  is reachable in a graph with edges, igraph returns NaN; CIGA returns zero for an
  edgeless graph. In/out mode changes path direction.
* Raw harmonic centrality is ``sum(1 / d(v,u))`` over reachable other vertices;
  unreachable vertices contribute zero. Normalized harmonic centrality divides by
  the full snapshot population ``n-1``, not just the reachable count.
* Eigenvector centrality uses igraph's eigenvector definition and optional max-one
  scaling. When permitted, a warned PageRank fallback is a different algorithm;
  inspect ``centrality_method`` or use ``pagerank=False`` to prohibit it.

Weights mean strengths for degree and eigenvector, but lengths for shortest-path
metrics. Weighted paths require strictly positive lengths. CIGA does not infer that
a large interaction strength should become a short distance: choose and record an
explicit transformation. The graph itself is built by summing selected pair events;
this aggregation is a modelling choice. See :doc:`analysis` and igraph's
`centrality API <https://python.igraph.org/en/1.0.0/api/igraph.GraphBase.html>`_.

Hypergraph participation
------------------------

Each observed group event has an identity, so repeated groups remain separate.
The incidence matrix ``I[v,e]`` is one if vertex ``v`` participates in event
``e``. Participation degree is ``sum_e I[v,e]`` and event-weight strength is
``sum_e I[v,e] * w[e]``. For directed events, tail and head incidence give out and
in participation; total incidence uses the union, so a vertex in both roles counts
once in total. A zero-weight event still counts in unweighted degree. Normalized
columns divide by ``n-1`` when ``n>1``; this is not a fraction of all possible
hyperedges. Weak incidence connectivity ignores direction, time and weights.
See :doc:`hypergraph` for examples, event identity and ordering.

Time and persistence
--------------------

Snapshot, window and cumulative analyses select events by ordered observed position;
a window width counts observed steps, not seconds. ``temporal_reachability`` is an
event-order property: ``strict=False`` permits paths within a simultaneous batch;
``strict=True`` permits a newly reached vertex to transmit only at a later step.
It ignores event weights, including zero. Marked memory-state tables retain actual
event presence separately from generated state rows. This does not demonstrate actual influence.

Graph persistence uses converted direct edge distances, not graph geodesic distances.
It symmetrizes directed inputs with a warning, takes the minimum converted distance
for repeated/opposite edges and omits self-loops. Missing sparse off-diagonal entries
represent infinite distances. This is not directed or hypergraph persistence. See
:doc:`analysis` for the conversion and :doc:`hypergraph` for why an incidence graph
is not automatically a higher-order model.

Recording a result
------------------

For each result preserve the input data or its hash, CIGA version and commit when
using development code, Python and backend versions, graph construction and time
selection, metric parameters, transforms, seeds and solver/convergence status.
DataFrame ``attrs`` are not preserved by CSV. When community membership is compared
across runs, compare partitions rather than numeric labels, which are arbitrary.

The repository example ``examples/scientific_reproducibility.py`` constructs a
small weighted temporal graph and writes results with their provenance to JSON under
``build/``. Run it from a checkout; for an installed release, record its exact
package version and distribution hash as well. A fixed seed helps repeatability
under a fixed environment, but does not guarantee identical results across backend
versions or concurrent callers.
