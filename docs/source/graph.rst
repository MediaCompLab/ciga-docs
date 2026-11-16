Graphs and temporal graphs
==========================

``TGraph`` stores time-indexed pair interactions and creates ``igraph.Graph``
objects for selected time points. It defaults to ``directed=True``. Start with
:doc:`tutorials` for construction, or :doc:`hypergraph` to preserve group events.

Construction
------------

Pass prepared data using the keyword ``data=``; the first positional argument of
``TGraph`` is an optional initial igraph object. Required columns are ``source``,
``target``, ``weight`` and the numeric columns named by ``positions``::

    import pandas as pd
    import ciga as cg

    pairs = pd.DataFrame({
        'scene': [1, 1, 2],
        'line': [1, 2, 1],
        'source': ['A', 'B', 'A'],
        'target': ['B', 'C', 'C'],
        'weight': [1., 2., 1.],
    })
    tg = cg.TGraph(data=pairs, positions=('scene', 'line'), directed=True)

Positions determine the resolution: ``('scene', 'line')`` identifies individual
lines; ``('scene',)`` groups a whole scene as one step. Order them coarsest first.
Within a selected graph, repeated pairs are represented by summed edge weights.

Selecting time
--------------

.. list-table:: Snapshot getter
   :header-rows: 1
   :widths: 45 55

   * - Call
     - Selection
   * - ``tg.get_graph((1, 2))``
     - Scene 1, line 2 only.
   * - ``tg.get_graph((1,))``
     - All lines in scene 1.
   * - ``tg.get_graph()``
     - All source interactions.
   * - ``tg.get_graph((2, 1), accumulate=True)``
     - All history through scene 2, line 1.
   * - ``tg.get_graph((2, 1), window_size=2)``
     - The most recent two observed steps through that bound.

A missing instantaneous selection, an empty window, or a window bound before the
first observation returns ``None``. A bound between observations uses only earlier
steps; a bound after the last observation ends at that last step. Check for ``None``
before calling a static analysis. A cumulative bound before the first observation returns
the initial graph (or an empty graph when none was supplied), including with
``mean_weight=True``. Returned graphs can be analyzed with ``graph_*`` functions or
igraph methods. ``get_graph`` rejects ``accumulate=True`` together with a window.

Numeric bounds are compared using the value they represent, including against large
integer positions. If a floating-point value has already rounded an intended integer,
use an integer bound instead to retain the original coordinate.

The ``tgraph_*`` analysis functions evaluate many snapshots. By default they use
cumulative history for raw events and separate snapshots for memory states produced
by ``accumulate_weights``. Pass ``accumulate=True`` or ``False`` explicitly to override
this choice. In those wrappers, ``window_size`` overrides accumulation.
``start`` and ``end`` bound the reported steps, not the cumulative history used
at each step; ``stride`` samples the selected steps. Supply full coordinate tuples
for analysis bounds. At line resolution, ``end=(1, float('inf'))`` includes all of
scene 1; a short ``end=(1,)`` does not have the getter's prefix-selection behavior.
For standard ``TGraph`` inputs, built-in sequential analyses take a private view of the
current event table at the start of each run, so edits between runs are reflected.
Custom callbacks, TGraph subclasses and inputs that cannot use this path continue to use
their existing getter behavior.

Standalone cumulative queries also reflect edits to ``tg.data`` made between calls,
including edits to previously queried events. To avoid reusing stale history, they
check the earlier events before reusing a compatible cache, or rebuild the selected
history when it cannot be checked safely. This can add work to repeated live queries.
If ``take_interval`` is overridden, the getter rebuilds the selected history rather
than making extra calls to the custom method for cache validation.

Weights and output
------------------

``get_graph`` transforms selected edge weights in this order:

1. ``mean_weight=True`` divides by the number of observed steps in the selection;
   this requires accumulation or a window.
2. ``w_normalized`` selects ``'max'``, ``'sum'``, ``'minmax'``, ``'max_abs'`` or
   ``'l1_abs'`` scaling.
   ``True`` means ``'max'``; ``False``/``None`` disables it.
3. ``invert_weight=True`` (or ``'reciprocal'``) applies ``1/(w + 1e-6)``;
   ``'max_minus'`` applies ``max(w) + 1e-6 - w``.

By default, event weights must be finite and nonnegative; edges with nonpositive
transformed weights are removed. The explicit ``weight_policy='signed'`` mode
retains negative balances and removes only exact zero edges from returned snapshots.
See :doc:`signed_weights` for subtraction, normalization and algorithm limits. Hypergraphs
retain zero-weight events, so the same options need not yield equivalent topology.
For metric result columns and weight interpretation, see :doc:`analysis`.
For HTML, GIF and MP4 output, see :doc:`visualization`.
For named raw relation layers and explicit sum/net projections, see :doc:`multilayer`.
``TGraph.positions`` returns the ordered time-axis names; ``metadata=`` stores copied
provenance, also available in returned graphs as ``ciga_metadata``.

API reference
-------------

.. currentmodule:: ciga

.. autoclass:: TGraph
   :members:
