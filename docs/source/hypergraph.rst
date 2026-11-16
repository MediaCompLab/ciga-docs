Hypergraphs and temporal hypergraphs
====================================

Use a hypergraph when one interaction involves a group. Each source row remains an
individual event with its participants, weight and metadata, even when the same
group occurs repeatedly. ``THypergraph`` adds time selection; ``Hypergraph`` represents
one selected collection of events. The core uses igraph incidence graphs and SciPy
sparse matrices and needs no optional native library.

Hypergraph support is included in CIGA 0.1.5; see :doc:`installation` and
:doc:`tutorials` for the graph/hypergraph workflow. Users of earlier source previews should
read :doc:`hypergraph_migration` for changed defaults and result columns.

.. contents:: On this page
   :local:
   :depth: 1

Dialogue preparation
--------------------

Keep each utterance as one event instead of expanding every speaker/listener pair::

    import pandas as pd
    import ciga as cg

    dialogue = pd.DataFrame({
        'scene': [1, 1, 2],
        'line': [1.5, 1.5, 7.5],
        'Speaker': ['A', 'A', 'B'],
        'Listener': ['B, C', 'B, C', 'C'],
        'weight': [2.0, 3.0, 1.0],
    })
    events = cg.prepare_hypergraph_data(dialogue, ['scene', 'line'],
                                       source='Speaker', target='Listener')
    th = cg.THypergraph(data=events, positions=['scene', 'line'])
    snapshot = th.get_hypergraph((1,))
    assert snapshot.ecount() == 2
    result = cg.hypergraph_degree_centrality(snapshot, weighted=True)
    print(result)

For directed data, ``tails`` are speakers and ``heads`` are listeners. Both must
be nonempty. For undirected data, ``members`` is their union. Participant strings
may be comma-separated names or Python list literals; collections are also accepted.
Special labels such as ``all`` are literal IDs and are not expanded automatically.
Preparation retains one row per event and canonical participant tuples in
``source``/``target``; ``members`` stores their union and directed data additionally
contains ``tails``/``heads``. Custom interaction/weight columns are copied to
``interaction``/``weight``. Other source columns remain available as metadata.

Constructing static hypergraphs
-------------------------------

``Hypergraph(data=...)`` accepts one row per event with ``members``, or with
``tails`` and ``heads`` when directed. ``event_id`` defaults to row ordinals;
``weight`` defaults to one. Other columns remain available through ``events``.
IDs must be hashable and nonmissing; event IDs must be unique. Groups are sets of
participants: repeating a participant inside one event does not add an incidence.

For a short edge-list construction::

    h = cg.Hypergraph.from_edges(
        [('A', 'B', 'C'), ('A', 'B', 'C'), ('D',)],
        event_ids=['utterance-1', 'utterance-2', 'utterance-3'],
        weights=[2, 3, 0],
        vertices=['isolated'],
    )
    assert h.vcount() == 5
    assert h.ecount() == 3
    incidence = h.incidence_matrix()
    strength = incidence @ h.events['weight'].to_numpy()

Empty events are rejected. Singleton events and explicit isolated vertices are
supported. Weights are finite and nonnegative. A zero-weight event remains in the
topology and counts toward unweighted participation degree.

The event table and backend exports are copies. Changing them does not mutate the
hypergraph. Reconstruct from ``Hypergraph(h.events, vertices=h.vertices,
directed=h.is_directed)`` when changing data; this also retains explicit isolates.
The event table is an export surface, not a promise that arbitrary Python IDs or
metadata can be serialized losslessly into every file format.

Metric definitions
------------------

* ``hypergraph_degree_centrality`` counts incident events. Its weighted columns
  sum their weights. Repeated groups count repeatedly. Directed ``out_degree``
  counts tail roles, ``in_degree`` head roles, and ``all_degree`` the union once per
  event. Thus all_degree need not equal in_degree+out_degree when roles overlap.
  Undirected results use ``degree``. ``normalized=True`` adds normalized columns
  by dividing by n-1, with zeros for n<=1. This is graph-style scaling, not a
  bounded fraction of possible hyperedges; repeated events can yield values >1.
  Both graph and hypergraph degree normalization yield one for a simple unweighted
  dyad; their n-1 divisor also applies when n=2.
* ``hypergraph_edge_sizes`` reports unique-member cardinality and order (size minus
  one), with additional tail/head sizes for directed events.
* ``hypergraph_connected_components`` and ``hypergraph_is_connected`` use weak
  incidence connectivity, ignoring direction, weight and time. Component labels
  are local to each snapshot. Connectivity of an empty vertex set is false.

``incidence_matrix()`` is binary, with rows in ``vertices`` order and columns in
``event_ids`` order. Directed ``role='tail'`` and ``role='head'`` give the two
role-specific matrices. The default union counts overlapping roles only once.

``to_bipartite()`` returns an igraph copy with ``type=False`` for original vertices
and ``type=True`` for event nodes. The ``vertex_id`` and ``event_id`` attributes
are separate namespaces. Synthetic ``name`` attributes prevent ID collisions.
Each incidence link carries its event's weight. These weights are not path lengths.
Link ``role`` attributes use ``members``, ``tails`` and ``heads``, matching the event
table's column names.

An igraph PageRank, eigenvector, Leiden or shortest-path result on this representation
is a graph result until a particular hypergraph definition is chosen. In particular,
directed incidence paths express a possible any-tail traversal; they do not require
all tail participants to be active. The methods in :doc:`hypergraph_backends` choose and identify their
definitions explicitly. Additional projections and TDA constructions remain planned work.

Time and windows
----------------

Time coordinates must be finite numeric columns (or named index levels), ordered
coarsest first. Row ordinals are assigned as event IDs before sorting. Full coordinate
tuples identify steps; short tuples select entire prefix groups.
NumPy floating-point bounds use the exact value they represent when compared with integer
coordinates. If a float has already rounded a large integer, that lost precision cannot
be recovered; pass an integer bound when adjacent large integer steps must remain distinct.

``get_hypergraph(point)`` returns events at that point or prefix. With no point it
returns all events. ``accumulate=True`` selects the whole history through the bound.
``window_size=2`` selects the most recent two observed steps through the bound,
including every simultaneous event. It does not subtract two from a numeric timestamp.
A bound before the first step produces an empty hypergraph, never a future event.

``accumulate=True`` and ``window_size`` are mutually exclusive on the snapshot getter.
The ``thypergraph_*`` analysis wrappers follow existing ``tgraph_*`` behavior: a window
overrides their default accumulation. Their ``start``/``end`` bounds limit reported
steps, while cumulative history still starts at the beginning; ``stride`` is applied
after selecting steps. Returned rows include the original time-coordinate columns::

    degrees = cg.thypergraph_degree_centrality(th, window_size=2, weighted=True)
    components = cg.thypergraph_connected_components(th, accumulate=False)
    sizes = cg.thypergraph_edge_sizes(th, start=(1,), end=(2,))

Explicit ``vertices=`` are retained in every snapshot, including empty ones. Without
that option only participants present in the selected events appear. Snapshot queries
use a sorted step index and construct independent objects; no mutable accumulation
cache or incremental streaming-update API is provided in this first implementation.

``get_hypergraph`` accepts ``w_normalized`` (False/None, True or max, sum, minmax),
``invert_weight`` (False/None, True or reciprocal, max_minus), and ``mean_weight``.
The last requires accumulation or a window, and divides by the number of observed
steps represented, including partial windows. Transformation order matches graph:
mean, normalization, inversion. Reciprocal uses 1/(w+1e-6); max_minus uses
max(w)+1e-6-w. Degree/eigenvector temporal wrappers expose ``w_normalized`` and
``mean_weight`` with graph defaults. These operate on individual event weights,
not aggregated pair/group weights. Repeated events and zeros remain in the topology,
including zeros produced by minmax normalization. An unweighted native algorithm
still requires explicit ``ignore_weights=True`` for nonunit transformed weights.

Geometric visualization
-----------------------

``hypergraph_viz`` draws a colored region around each explicit member set: circles
for singleton events, rounded capsules for dyads, and padded convex hulls for larger
sets. Identical sets share a region and an event count for display only; directed
groups retain separate tail and head sets. Member order within each role is irrelevant.
Input events, IDs, weights and metadata are unchanged. Exact membership is shown in
the legend and highlighted on selection: spatial overlap or enclosure alone does
not establish membership. Region area/color does not encode weight or centrality.

The standalone HTML has group and participant selection, paginated source events,
and keyboard-accessible controls. Selecting a directed group shows speakers/tails
through a visual junction to listeners/heads, including overlapping roles. This
junction is a drawing device, not an additional actor or a propagation model.
The original IDs and selected metadata are rendered as text. File exports are
self-contained and need no external JavaScript or optional hypergraph backend.
Disable the graph-style browser launch default for unattended export::

    import ciga as cg

    h = cg.Hypergraph.from_edges([
        ['Sheldon', 'Leonard', 'Penny'],
        ['Sheldon', 'Leonard', 'Penny'],
        ['Leonard', 'Penny'],
    ])
    path = cg.hypergraph_viz(h, output_file='groups.html', title='Dialogue groups', open_browser=False)
    cg.hypergraph_viz(h, output_file='groups.svg', open_browser=False)
    cg.hypergraph_viz(h, output_file='groups.png', open_browser=False)

Paths ending in ``.html``, ``.png``, ``.svg`` or ``.pdf`` select the format and the
function returns the absolute path as a string. Static figures list roles in their
legend. Exports use Matplotlib without changing its global backend or creating
pyplot-managed figures. ``pos`` accepts a mapping from every vertex ID to finite
2D coordinates, normalized to fit the canvas. The default uses an igraph incidence
Kamada-Kawai layout with a local seeded initializer and node separation. Layout
distances have no analytical meaning; supply ``pos`` for controlled figure layouts.

``thypergraph_viz`` uses the same launch defaults as ``tgraph_viz``: port=8050,
open_browser=True, blocking=True. It returns HTTPServer. ``output_file='view.html'``
or ``port=None`` selects offline export and returns an absolute path string.
``hypergraph_viz(port=N)`` also supports an asynchronous HTML server. For servers
started with nonblocking calls, use ``server.shutdown(); server.server_close()``.
Servers bind to loopback and serve only the generated view. A blocking server closes
on Ctrl+C. ``time_mapping``, ``time_label_column`` and ``time_mapping_strict`` accept
the same DataFrame, mapping and callable forms as the graph viewer.

The timeline uses one layout and one group-color catalog for the entire source.
It shows cumulative history by default. ``accumulate=False`` selects snapshots,
with inactive vertices muted; ``window_size=N`` selects the last N observed steps
and overrides accumulation, as the temporal analyses do. Equal-time events remain
together. ``start`` / ``end`` bound the displayed frames while cumulative/window
history retains its usual semantics. The entire source catalog is embedded even
when frames are bounded. More than ``max_frames=300`` raises before rendering;
narrow the bounds, use coarser time positions, or explicitly raise the limit.
Export a chosen ``THypergraph.get_hypergraph`` snapshot through ``hypergraph_viz``
for static PNG/SVG/PDF output. These viewers are for selected scenes or subgraphs;
layout and embedded event tables are not a million-event rendering pipeline.

Local dialogue CSV example
--------------------------

The repository includes ``m_data.csv`` and ``BB_F4_with_speakers_listeners.csv``.
The reproducible script ``examples/hypergraph_dialogue.py`` reads both, compares
the graph and hypergraph pipelines, and writes interactive groups, directed timelines,
PNG/SVG figures, degree tables and a report under ``build/hypergraph-dialogue-demo``.
Run from a checkout with CIGA installed::

    python examples/hypergraph_dialogue.py

To include native research analyses, install ``.[hypergraph]`` and run::

    python examples/hypergraph_dialogue.py --native

The supplied annotations give these results:

.. list-table:: Same source events, two representations
   :header-rows: 1

   * - Input
     - Rows / actors
     - Undirected / directed groups
     - Expanded pairs / distinct directed edges
   * - ``m_data.csv``
     - 322 / 10
     - 9 / 31
     - 1,027 / 48
   * - ``BB_F4_with_speakers_listeners.csv``
     - 52 / 2
     - 1 / 2
     - 52 / 2

These are supplied TV-dialogue annotations, not an independent large movie corpus.
Each annotation row remains one event. Hypergraph degree counts participation once
per row; graph strength sums unit weights over expanded speaker-listener pairs,
including pairs within a multi-party event. For example, Leonard participates in
317 events but has graph pair strength 654. The different units are explicit in the
comparison CSV. The five-person group occurs in 147 rows; its identity is visible
in the hypergraph even when pairwise summaries discard that grouping.

The first timeline uses 12 scene frames; the second uses 18 shot frames. Native
Reticula analysis uses full scene/line and scene/shot/line coordinates, respectively,
mapped to 322 and 52 ordinal steps. Shot is included because Line resets between
shots; subtitle time strings are not silently interpreted as seconds. These
display resolutions are explicit constructions of separate ``THypergraph`` objects.

With ``--native``, the generated report records backend versions, input hashes,
parameters, seeds and solver outcomes. Some fits on these samples do not converge;
inspect the report before interpreting centrality or community results. These small
examples demonstrate representations, not validation on a large movie corpus.

Minimal scene-view construction with the first CSV::

    import pandas as pd
    import ciga as cg

    raw = pd.read_csv('m_data.csv')
    prepared = cg.prepare_hypergraph_data(raw, directed=True)
    scenes = cg.THypergraph(prepared, ['Season', 'Episode', 'Scene'], directed=True)
    cg.thypergraph_viz(scenes, output_file='scenes.html', title='Speakers and listeners',
                       accumulate=False, open_browser=False)

Optional native libraries
-------------------------

See :doc:`hypergraph_backends` for XGI centralities, Hypergraphx communities and
Reticula reachability, including conversions, mathematical assumptions and provenance.

API consistency and migration
-----------------------------

See :doc:`hypergraph_migration` for preview parameter aliases, changed defaults and
intentional differences from graph/tgraph.

API reference
-------------

The full signatures and class methods are in :doc:`hypergraph_reference`.

.. toctree::
   :maxdepth: 1

   hypergraph_backends
   hypergraph_migration
   hypergraph_reference
