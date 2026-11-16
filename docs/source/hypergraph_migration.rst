Hypergraph API migration
========================

The common workflow and options follow graph/tgraph. Static ``Hypergraph`` remains
undirected by default, matching ``igraph.Graph``. ``THypergraph`` and dialogue
preparation now default to ``directed=True``, matching ``TGraph``. Use explicit
``directed=False`` for undirected temporal event tables.

CIGA 0.1.5 includes the following changes from the earlier source preview:

.. list-table:: Migration from the initial hypergraph preview
   :header-rows: 1
   :widths: 25 35 40

   * - Surface
     - Current graph-style interface
     - Migration / preservation
   * - Dialogue columns
     - ``source``, ``target``, ``interaction``, ``weight``, ``positions``, ``dropna``
     - ``speaker_col`` / ``listener_col`` remain deprecated aliases. Speaker/Listener
       are fallback names when canonical source/target columns are absent.
   * - Missing participants
     - ``dropna=True`` drops missing source/target rows.
     - To retain an undirected singleton from a missing role, pass
       ``directed=False, dropna=False``. IDs are assigned before filtering/sorting.
   * - Static vertex centralities
     - Degree, eigenvector and Katz return metric columns in ``h.vertices`` order.
     - ``include_character=True`` restores an ID column. IDs are also in
       ``result.attrs['vertex_ids']``. Communities retain character/community columns.
   * - Directed degree columns
     - ``in_degree``, ``out_degree``, ``all_degree`` and weighted counterparts.
     - Rename preview ``degree`` to ``all_degree`` and ``weighted_degree`` to
       ``weighted_all_degree``. Event-union counting is unchanged.
   * - Temporal results
     - Time columns, then ``character``, then metric columns.
     - Event-size and joint node/event tables retain their own event/entity IDs.
   * - Eigenvector output
     - ``scale=True`` and ``centrality_method`` match graph conventions.
     - Pass ``scale=False`` for the original XGI normalization. Backend metadata
       is in attrs; ``include_provenance=True`` adds backend/version/method columns.
   * - Community iteration budget
     - ``n_iterations=500``, ``seed=None``.
     - ``max_iter`` is a deprecated alias for this model. Set a seed explicitly
       for reproducibility. XGI's native solver option remains ``max_iter``.
   * - Visualization
     - ``output_file``, ``port``, ``open_browser``; temporal launch also has ``blocking``.
     - ``output_path`` and the temporal positional filename remain deprecated aliases.
       File mode returns an absolute path string, server mode returns HTTPServer.

Aliases emit ``DeprecationWarning``; conflicting canonical and alias values raise.
Default/schema changes are explicit preview migrations, not silent compatibility
inference. Static centrality IDs can be recovered with ``include_character=True``;
the original native eigenvector table additionally needs ``scale=False`` and
``include_provenance=True``. Hypergraph-only backend metadata, weighted-event
semantics and explicit empty snapshots remain available. Existing graph/tgraph
implementations and their callers have not been changed.

Common signatures do not imply interchangeable algorithms. Hypergraph eigenvector
rejects ``weighted=True``, ``return_eigenvalue=True`` and ``pagerank=True`` because
the selected native methods do not provide those behaviors. Its ``pagerank=False``
default intentionally preserves strict method selection. Connectivity accepts
``mode='weak'``; stronger activation/path semantics require a separately defined
algorithm. No graph projection, zero-event deletion, or placeholder result is added
to make an unsupported option appear to work.
