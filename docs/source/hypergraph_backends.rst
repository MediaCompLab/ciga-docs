Native hypergraph libraries
===========================

For construction and basic metrics, start with :doc:`hypergraph`. See
:doc:`installation` for all extras and :doc:`hypergraph_reference` for signatures.

The core graph, temporal graph and incidence-based hypergraph APIs still support
Python >=3.9. XGI/HGX require Python >=3.10; Reticula 0.13 requires Python >=3.12.
For all three backends, use Python >=3.12 and install from this checkout::

    python -m pip install -e '.[hypergraph]'

Individual extras are ``hypergraph-reticula``, ``hypergraph-xgi`` and
``hypergraph-hgx``. Supported dependency ranges are Reticula >=0.13,<0.14,
XGI >=0.10.2,<0.11 and Hypergraphx >=1.8,<1.9. The local reference tests use
0.13.0, 0.10.2 and 1.8.0 respectively. CI checks the integrations separately on
Python 3.12/3.13 and Windows/Linux/macOS, with XGI/HGX also checked on Python 3.10.
Reticula's wheels advertise >=3.10 but contain Python 3.12-only f-string syntax.
The adapter rejects older Python with an actionable ImportError before import.
On Python 3.10/3.11, install ``.[hypergraph-xgi,hypergraph-hgx]``.

The existing ``all`` extra retains its Python 3.9 support; request
``.[all,hypergraph]`` to combine it with these integrations. Requested backends
are never silently omitted with Python-version markers. Missing dependencies
raise an installation message only when their conversion or analysis is called.

``import ciga`` and ordinary ``graph_*`` / ``tgraph_*`` calls do not import the
hypergraph implementation or its optional libraries. Public hypergraph names are
loaded lazily. Hypergraph code owns its time types and snapshot driver; it never
calls or modifies the graph/tgraph analysis driver, weight transforms, or RNG setup.

Native data views
-----------------

Conversion functions return a ``HypergraphBackendView``. Its ``network`` is the
actual third-party object and can be passed directly to that library's algorithms
and supported file-format writers. The view also provides:

* ``vertex_ids``: native integer ID -> original CIGA vertex ID.
* ``event_ids``: native edge key -> tuple of original event IDs.
* ``events``: an independent source table retaining metadata, weights and event IDs.
* ``time_points``: Reticula numeric time -> original position tuple.
* ``losses``: transformations explicitly requested for the native representation.

For example, after installing the XGI extra::

    import ciga as cg

    h = cg.Hypergraph.from_edges([['A', 'B'], ['B', 'C']])
    view = cg.hypergraph_to_xgi(h)
    native = view.network  # xgi.Hypergraph or xgi.DiHypergraph
    assert native.num_edges == h.ecount()

Native mutations affect the exported object, not CIGA. They do not synchronize its
ID maps or source table. This is an export interface; arbitrary Python metadata
and IDs are not guaranteed to round-trip through every third-party file format.

XGI preserves distinct hyperedge IDs, including repeated groups. Node attributes
contain ``ciga_vertex_id``; edge attributes include ``weight``, ``ciga_event_id`` and
``ciga_metadata``. Storing a weight attribute does not imply an algorithm uses it.

Reticula merges identical native edges, including equal-time temporal events.
``hypergraph_to_reticula`` and ``thypergraph_to_reticula`` reject this by default;
``duplicates='collapse'`` explicitly permits it while retaining all original IDs
in the sidecar map. Reticula views require unit event weights unless
``ignore_weights=True``. Even a zero-weight event then remains in the topology.

Hypergraphx conversion supports directed roles and event weights. Repeated groups
raise by default; ``duplicates='sum'`` aggregates their weights, with all source
IDs retained in the edge's ``ciga_event_ids`` metadata and the sidecar map. The
adapter does not invent a rule for merging arbitrary event metadata.

Native centrality and communities
----------------------------------

The XGI wrappers require undirected data and unit weights, or an explicit
``ignore_weights=True``. No implicit graph projection or PageRank fallback occurs.

* ``hypergraph_eigenvector_centrality(method='h'|'z'|'clique', **kwargs)`` calls
  the corresponding XGI formulation. The default is ``h``. Native arguments such
  as ``tol`` and ``max_iter`` are forwarded; ``seed`` is supported by ``h``.
  ``scale=True`` rescales the largest score to one; False keeps XGI normalization.
  Default columns are eigenvector_centrality and centrality_method in vertex order.
  Each native function has its own mathematical domain and accepted arguments.
* ``hypergraph_katz_centrality(cutoff=100)`` uses XGI's walk and attenuation convention.
* ``hypergraph_node_edge_centrality(**kwargs)`` calls XGI's nonlinear joint metric.
  The result contains ``entity`` (``vertex`` or ``event``), original ``id`` and
  ``centrality``. Native nonlinear functions and solver options can be supplied.

Undefined/non-finite results raise. XGI's iteration-limit warning becomes a
``RuntimeError``; other solver errors propagate. These are method wrappers, not
claims that the underlying algorithms run in linear time or fit every corpus in memory.
See `XGI's centrality definitions and references
<https://xgi.readthedocs.io/en/stable/api/algorithms/xgi.algorithms.centrality.html>`_.

``hypergraph_community_hy_mmsbm(h, n_communities, ...)`` fits Hypergraphx's native
Hy-MMSBM. Its Poisson model requires positive integer count weights, undirected
events, and event sizes >=2. Singleton events are rejected rather than dropped.
Use ``duplicates='sum'`` to interpret repeated dialogue groups as counts. Arbitrary
interaction strengths or sentiment scores are not count observations.

The result preserves raw ``membership_0``, ... model intensities, an argmax
``community`` label, and ``converged``. Intensities are not normalized probabilities.
A zero-membership row has an undefined label. An iteration-limited fit warns and
remains explicitly unconverged; inspect that status before interpretation. Static
results additionally retain the affinity matrix and iteration count in ``attrs``.
The seed, iteration limit, tolerance, convergence-check interval and assortative
model option are configurable. See the `Hypergraphx documentation
<https://hypergraphx.readthedocs.io/en/latest/>`_ for the model and other native methods.

A small example with no singleton events::

    research_h = cg.Hypergraph.from_edges([
        ['A', 'B', 'C'], ['A', 'B', 'C'], ['B', 'C', 'D'], ['A', 'D'],
    ])
    scores = cg.hypergraph_eigenvector_centrality(research_h, method='h', seed=7,
                                                max_iter=1000)
    joint = cg.hypergraph_node_edge_centrality(research_h)
    communities = cg.hypergraph_community_hy_mmsbm(research_h, 2, duplicates='sum',
                                                  seed=7, n_iterations=500)
    print(communities[['character', 'community', 'converged']])

Each of these four static functions has a ``thypergraph_*`` counterpart with the
same snapshot/window/bound options as basic measures. Fits are independent across
snapshots; community labels are not longitudinal identities. Eigenvector/Katz default
to graph-style metric columns with backend/version/method in attrs; set
``include_provenance=True`` to include those columns. Joint centrality, communities
and reachability retain their specialized diagnostic/provenance columns. Temporal
results preserve per-snapshot metadata in ``attrs['snapshots']``; convergence remains
a column for every community row. CSV exports omit pandas attrs, so explicitly
request provenance columns or save the attrs separately for exported centralities.

Native temporal reachability
----------------------------

``thypergraph_to_reticula`` and ``thypergraph_temporal_reachability`` require an
explicit ``time_mode``:

* ``ordinal`` maps distinct observed steps to 0, 1, ...; events at the same step
  retain the same time. Waiting time measures steps, not elapsed physical time.
* ``coordinate`` requires exactly one numeric position and uses its original units.
  Values that would lose precision when converted to Reticula double timestamps
  are rejected, including large integer timestamps that cannot be represented exactly.

``source``, ``start`` and optional positive ``waiting_time`` select a Reticula
``out_cluster`` query. ``start`` is a number in the chosen units, not a hierarchical
tuple. For ordinal time, start at -1 to allow the event at ordinal zero. The result
contains every original vertex, ``reachable``, ``arrival_time`` (NaN if unreached),
``time_mode`` and method provenance. The source is reachable at the starting time.

Directed transmission follows Reticula's any-tail rule: one reached tail can activate
the event and reach its heads; this does not reach otherwise unreached co-tails.
Event-to-event transmission requires strictly increasing times. Simultaneous events
cannot relay one another and are never artificially separated. Limited waiting time
also applies from the source's start time to its first usable event. See
`Reticula temporal reachability
<https://docs.reticula.network/algorithms/temporal_network_reachability.html>`_.

For example::

    import pandas as pd

    temporal_events = pd.DataFrame({
        'time': [1., 2., 2.],
        'tails': [('A',), ('B',), ('C',)],
        'heads': [('B',), ('C',), ('D',)],
    })
    temporal = cg.THypergraph(temporal_events, ['time'], directed=True)
    reached = cg.thypergraph_temporal_reachability(temporal, 'A', 0.,
                                                   time_mode='coordinate')
    assert set(reached.loc[reached.reachable, 'character']) == {'A', 'B', 'C'}
