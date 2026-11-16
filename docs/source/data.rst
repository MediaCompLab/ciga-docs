Data preparation
================

CIGA works with pandas DataFrames. Read files with pandas (for example,
``pd.read_csv``), prepare the interaction table, then construct a graph or
hypergraph. CIGA does not provide a separate CSV/Excel/JSON file-loading API.
See :doc:`tutorials` for a complete example.

Required columns
----------------

.. list-table:: Input contract
   :header-rows: 1
   :widths: 25 75

   * - Column / option
     - Meaning
   * - ``positions``
     - Numeric time columns, ordered coarsest first, such as season, scene, line.
       Use all levels needed to distinguish steps when line numbers reset.
   * - ``source``, ``target``
     - Speaker and listener IDs. Pass the actual column names to the preparation function.
       A participant cell may contain a name, a Python list, or comma-separated names.
   * - ``interaction``
     - Text or other input to ``calculate_weights``; unnecessary if weights are supplied.
   * - ``weight``
     - An existing numeric weight column, or a column created by ``calculate_weights``.
       ``TGraph`` requires it; hypergraph preparation defaults missing weights to one.
   * - ``dropna=True``
     - Drop rows with missing source or target values during preparation.

Choose whether to expand groups
-------------------------------

``prepare_data`` expands each source-target combination into a separate pair row.
``prepare_hypergraph_data`` keeps one row per event and preserves the member sets.
Do not pass an already expanded pair table if you want to preserve original group
identity. See :doc:`hypergraph` for directed roles and missing-participant handling.

For CSV cells that contain quoted Python list literals, such as ``['A', 'B']``,
convert them to actual lists before graph preparation; the graph parser otherwise
retains quote characters in IDs. Hypergraph preparation parses this format directly.
Use numeric positions for computation; human-readable labels belong in a viewer's
``time_mapping`` (:doc:`visualization`).

Weights and aggregation
-----------------------

Continue with ``dialogue`` and ``positions`` from :doc:`tutorials`::

    pairs = cg.prepare_data(dialogue, positions, source='Speaker', target='Listener', interaction='text')
    counts = cg.calculate_weights(pairs, weight_func=lambda text: 1)
    scene_pairs = cg.agg_weights(counts, positions=('scene',))
    tg = cg.TGraph(data=scene_pairs, positions=('scene',), directed=True)

``calculate_weights`` defaults to ``len(interaction)``. Pass a function explicitly
when you mean counts, word counts or another measure. ``agg_weights`` sums weights
by position and source-target pair by default; use it to choose a coarser resolution.
For graph data, ``TGraph`` also sums repeated pair weights in each selected graph.
For hypergraphs, repeated events remain separate and count separately.

``weighted=True`` selects a metric's use of weights. ``w_normalized`` rescales the
input weights, while ``normalized=True`` requests a metric-specific normalization.
They are different operations; see :doc:`analysis` before interpreting scores.

Decay as a data preparation step
--------------------------------

``accumulate_weights`` operates on a pairwise event DataFrame; it is not an option
of ``TGraph`` or of centrality functions. Its output contains an accumulated
weight for each pair at each generated step. You can construct a new ``TGraph``
from those values and use its snapshots with graph metrics, visualizations or
other consumers that accept a TGraph::

    import pandas as pd
    import ciga as cg

    events = pd.DataFrame({
        'step': [1, 2, 3], 'source': ['A', 'B', 'B'],
        'target': ['B', 'C', 'C'], 'weight': [10., 1., 1.],
    })
    states = cg.accumulate_weights(events, positions=('step',),
                                   decay=0.5, ltm_rate=0)
    decayed = cg.TGraph(data=states, positions=('step',))
    snapshot = decayed.get_graph((3,), accumulate=False)
    degrees = cg.tgraph_degree_centrality(decayed, accumulate=False, weighted=True)

At step 3 the ``A`` to ``B`` weight is 2.5. Temporal graph analyses recognize the
state table and use snapshots by default. Passing ``accumulate=True`` explicitly
sums the successive states again and gives 17.5 for that pair. Window and mean modes
also combine these states; they do not automatically implement a decaying event
window. Some graph algorithms ignore weights or have restrictions on their domain;
choosing the state table does not change the metric's definition.

Position names may refer to ordinary columns or named index levels, including a
MultiIndex; the optional ``time`` axis also accepts a named index level. If a name
exists in both places, the column takes precedence. ``source``, ``target`` and
``weight`` must remain columns. The input is not modified, and the returned table
contains position columns as before. For example, to decay once per episode even
when the input is indexed by episode and line::

    indexed = pd.DataFrame({
        'episode': [1, 1, 2, 3], 'line': [1, 2, 1, 1],
        'source': ['A', 'A', 'A', 'A'], 'target': ['B', 'B', 'B', 'B'],
        'weight': [6., 4., 0., 0.],
    }).set_index(['episode', 'line'])
    episode_states = cg.accumulate_weights(indexed, positions=('episode',),
                                           decay=0.5, ltm_rate=0)
    # A -> B weights are 10, 5, 2.5 over episodes 1, 2, 3.
    episode_graph = cg.TGraph(data=episode_states, positions=('episode',))

Including ``line`` in ``positions`` advances decay at each observed episode/line
combination instead. Repeated or unnamed index levels cannot identify a requested
coordinate; assign unique level names or supply the coordinate as a column.

With ``time=None``, one decay step corresponds to one distinct observed position,
not an elapsed physical interval. For exponential decay, the short-term state is
``S_t = (1-decay) * S_(t-1) + X_t``; the returned weight also adds
``ltm_rate * cumulative_sum(X)``. The default ``ltm_rate=0`` returns only the
short-term state. Setting ``ltm_rate=1`` also adds the undiscounted cumulative sum;
with ``decay=0`` this doubles the cumulative sum. Linear and power-law kernels have
different meanings.

The output includes a reserved boolean column ``_ciga_observed_event``. It is true
where an input pair actually interacted at that step, including zero-weight events;
other rows describe memory alone. Core temporal reachability uses this marker to
avoid inventing events. Keep the column intact when saving or transforming the states;
CSV and pickle round-trips preserve it. If it is lost or no longer represents the
original events, pass the original event table using ``data=`` to reachability
functions. The marker also selects the automatic snapshot default; a table without it
is treated as raw interaction data. Do not feed state tables back into
``accumulate_weights``; start from the original interactions.

The optional ``time`` argument currently casts non-integer times to integers. The
resulting integer time and position tuple must map one-to-one; ambiguous mappings
raise ``ValueError`` rather than mislabel events. Gaps can produce rows without a
corresponding position; do not assume that it
faithfully models arbitrary continuous or irregular physical times. Inspect the
returned table before constructing a graph. Preprocessing expands every pair across
the global axis and can add zero rows before a pair's first interaction. In signed
TGraphs those rows can introduce vertices early even when the corresponding zero edge
is absent. Preprocessing does not preserve arbitrary event annotations or decay an initial graph. It is
not a general transformation of every possible TGraph or of hypergraph events.
For undirected interactions, consistently orient pair IDs before preprocessing.
These boundaries are significant when interpreting topology and normalized metrics.

Files and listener inference
----------------------------

For your own data, replace the in-memory table with ``pd.read_csv('dialogue.csv')``.
Export a result with ``result.to_csv('results.csv', index=False)``. pandas ``attrs``
are not stored in CSV; save native hypergraph provenance separately or request
``include_provenance=True`` where supported.

``infer_listeners`` fills in listener annotations using a configured model client.
It requires the ``llm`` extra, credentials and a model name accepted by your provider;
calling it sends dialogue to that provider. The checkout example
``ciga/examples/ex_infer_listeners.py`` shows the required columns and client setup.
Review the annotations before using them as observed interaction data.

API reference
-------------

.. currentmodule:: ciga

.. autofunction:: prepare_data
.. autofunction:: segment
.. autofunction:: calculate_weights
.. autofunction:: agg_weights
.. autofunction:: accumulate_weights
.. autofunction:: normalize_weights
.. autofunction:: invert_weights
.. autofunction:: infer_listeners

