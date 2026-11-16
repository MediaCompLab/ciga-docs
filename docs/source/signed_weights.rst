Signed graph weights (development checkout)
===========================================

This opt-in Graph/TGraph feature retains positive and negative interaction
contributions. It uses igraph; no new dependency or Python-version requirement is
introduced. It is a source change, not a statement that a new package has shipped.

Construction and a complete example
-----------------------------------

``TGraph`` accepts ``weight_policy='positive'`` (default) or ``'signed'``. All event
weights must be finite real numbers. Negative events require signed mode; older
positive-only handling of negative events was query-order dependent and is no
longer accepted for new objects. Valid nonnegative inputs keep their existing
positive-mode results, including the old zero-edge and min-max behavior.

This example forms a net graph before computing incoming relative strength::

    import pandas as pd
    import ciga as cg

    def layer(weights):
        return cg.TGraph(data=pd.DataFrame({
            'time': [1, 2, 3], 'source': ['A', 'A', 'A'],
            'target': ['B', 'B', 'B'], 'weight': weights,
        }), positions=['time'])

    pos = layer([3, 0, 4])
    neg = layer([0, 5, 0])
    net = cg.subtract_tgraphs_by_weight(pos, neg, weight_policy='signed')
    graph = net.get_graph((3,), accumulate=True)  # A -> B has net weight 2
    prominence = cg.tgraph_degree_centrality(
        net, accumulate=True, weighted=True, w_normalized='max_abs')
    print(prominence[['time', 'character', 'weighted_in_degree']])

The raw cumulative balances are 3, -2 and 2. For B, the maximum-absolute-normalized
incoming strengths are 1, -1 and 1. Signed strength is a net sum, not a probability
or a nonnegative share. Node strength can exceed the range of individual normalized
edges when several edges enter that node. This example defines a computation, not
a validation of any psychological interpretation.

State and transformations
-------------------------

The raw signed accumulator retains negative and zero balances. Queries, including
windows, backwards queries and normalization, do not clip that cache. Returned
signed snapshots remove exact zero edges but keep observed vertices. Zero event
rows retain their time and node support. An empty instantaneous selection still
returns ``None``; an observed zero-only step returns an edgeless graph with nodes.
The initial graph contributes only to cumulative queries, as in the existing API;
instantaneous/window queries and interval sums use selected events alone.

* ``max_abs`` divides by the maximum absolute edge weight.
* ``l1_abs`` divides by the sum of absolute edge weights.
* Both preserve signs, handle all-zero input as zero and avoid denominator overflow
  for finite inputs by scaling first. Arithmetic that itself overflows is rejected.
* ``normalize_weights`` supports both methods globally or per position group.
* ``True`` still means legacy ``max``. On a negative signed snapshot, ``max``,
  ``sum`` and ``minmax`` are rejected: use an absolute-denominator method or no
  normalization. The standalone DataFrame's old methods retain their old behavior;
  min-max scaling there is an explicit unsigned transformation.
* Weight inversion rejects negative inputs. Supply a separately defined
  nonnegative distance/cost view for path analysis; negative sentiment is not
  automatically a negative distance.

``get_delta_graph`` without ``dw_normalized`` sums event contributions in
``(start, end]`` for a full start coordinate. With ``dw_normalized``, it retains the
legacy difference of instantaneous/prefix endpoint snapshots, not cumulative
snapshots. That endpoint mode does not permit ``mean_weight=True``. Signed delta
results preserve negative edges; do not confuse these two delta definitions.

Arithmetic and metadata rules
-----------------------------

Static add/subtract and ``TGraph.graph_sub`` share name-aligned dyad arithmetic.
Parallel edges and self-loops contribute once each before arithmetic. Temporal
operations sum duplicate time/source/target keys before joining, preventing a
many-to-many merge from multiplying contributions. Signed subtraction includes
right-only dyads as negative values. Exact zero static edges are omitted; temporal
zero rows retain observed support. Signed static subtraction preserves isolates
unless ``drop_isolated_nodes=True`` is explicitly supplied.

Policies are inherited when both inputs agree. Untagged igraph objects default to
positive mode; mixed policies require an explicit ``weight_policy``. TGraph
snapshots carry the graph attribute ``weight_policy``. The instance method
``TGraph.graph_sub`` uses its TGraph's policy unless overridden. Default positive
subtraction remains the legacy positive part on left support, including event-level
clipping in the temporal helper; request signed mode for true net arithmetic.

Inputs must have the same directedness. Temporal inputs also require identical
ordered position columns; matching units and clocks remain the caller's
responsibility. Non-weight graph/vertex/edge attributes use the first input's first
value on conflict. Temporal arithmetic carries only position/source/target/weight
event columns and combines the initial graphs separately. It does not merge
arbitrary event annotations or automatically preserve custom subclasses.
``tgraph_filter_edges`` retains the policy and copies the initial graph; it filters
event rows, not the initial graph. Operations return independent graph objects.

New pickles retain the policy and rebuild the derived cache on loading. Old
pickles without the policy load as positive mode with a cold cache, preserving
their compatibility behavior. To adopt signed semantics for an older object,
reconstruct a new signed TGraph from its original event table and initial graph;
do not reuse an old clipped cache or change private fields.

Analysis support and boundaries
-------------------------------

Weighted degree/strength supports finite signed weights, including temporal
windows and stride. Existing weighted column names and degree normalization are
unchanged. Unweighted metrics use the returned nonzero topology and ignore signs.

Weighted betweenness, closeness, harmonic centrality and diameter require strictly
positive lengths. Weighted eigenvector/PageRank requires nonnegative weights;
negative input is rejected before any fallback. Betweenness solver failures
propagate instead of becoming fabricated zeros. Weighted degree, betweenness,
closeness and harmonic centrality reject nonempty graphs without a ``weight``
edge attribute; edgeless graphs need no edge weights.

Louvain and label propagation reject negative weights. Leiden CPM forwards finite
signed weights to the backend; other objectives require nonnegative input. CPM's
signed execution is tested with local python-igraph 1.0.0, not all backend versions
and configurations. Existing backend restrictions on directed graphs still apply.
Rips distance conversion rejects negative weights before distance inversion.

This development checkout does not add a signed spectral model, Bellman-Ford path
API or signed hypergraphs. :doc:`multilayer` describes ``TMultiLayerGraph`` for
retaining original layers and making explicit linear projections; a net scalar
cannot recover cancellation between them. ``analysis_capabilities()`` and
``get_analysis_capability()`` expose the shared weight-domain rules programmatically.

Sign-resolved strength
----------------------

``graph_signed_strength(g)`` returns positive magnitude, negative magnitude, net
and absolute strength for each vertex. Directed graphs have in/out/all columns,
for example ``positive_in_strength``, ``negative_in_strength``, ``net_in_strength``
and ``absolute_in_strength``. Undirected graphs use ``positive_strength``, etc.
Negative magnitude is nonnegative: positive=5 and negative=3 give net=2 and
absolute=8. Loops contribute twice in undirected/all strength and once in in/out.

``tgraph_signed_strength`` uses the same time driver as other centrality wrappers::

    strength = cg.tgraph_signed_strength(net, w_normalized='max_abs')
    print(strength[['time', 'character', 'positive_in_strength',
                    'negative_in_strength', 'net_in_strength', 'absolute_in_strength']])

Replace ``time`` with the actual position column(s). Windows, stride, bounds and
mean weights are supported. ``normalized=True`` appends columns divided by n-1,
returning zero normalized values when n <= 1; these are not probabilities.
Nonempty inputs require finite real edge weights; missing weights raise an error.

This decomposes the current snapshot's edge signs. If +5 and -5 contributions
have already cancelled within one dyad, neither positive nor negative historical
contribution can be recovered by this function. Preserve original layers/events
for that question. Existing degree result columns remain unchanged.

Signed labels and visual outputs
--------------------------------

Signed HTML views preserve the classic straight, neutral-colored edges and uniform
edge width. Only numeric edge labels encode sign: green (``#008000``) for positive,
red (``#d62728``) for negative, with explicit +/− signs. The label color controls
are independent of the original edge-color control. Bidirectional pairs retain
one line and two arrowheads; each direction's number gets its own color. Parallel
edge contributions are listed individually in the same label; none is silently
discarded. Exact zero edges are omitted from the displayed edge topology.

SVG export retains straight edges, both direction arrows, separately colored
numbers, labels and self-loops. GIF/MP4 use neutral straight edges and green/red
numeric labels as well. Natural self-loops remain loops. Signed animation uses
actual snapshots, including edges that later cancel, rather than the positive-only
fast accumulator. This costs more rendering time on large signed graphs.

Visual layout and cross-frame intensity reference use the union of historical
absolute contributions through the selected end, rather than the possibly
cancelled final graph. This is only a layout/display reference; it does not alter
the analyzed graph. Animation node intensity and top-node ranking use absolute
incoming strength (undirected: absolute strength), not a clipped negative net
value. Node layout stays fixed across frames. HTML still requires vis-network
from its existing CDN; no new dependency or offline-runtime promise is introduced.
