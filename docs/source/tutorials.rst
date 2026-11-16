Getting started
===============

After :doc:`installation`, run the examples below in order. They use an in-memory
table, need no optional libraries, and do not contact a model provider.

1. Prepare pairwise interactions
--------------------------------

Each row below is one line of dialogue. ``positions`` determines the analysis
resolution; using only ``scene`` makes each observed scene one time step::

    import pandas as pd
    import ciga as cg

    dialogue = pd.DataFrame({
        'scene': [1, 1, 2, 2],
        'line': [1, 2, 1, 2],
        'Speaker': ['Alice', 'Bob', 'Alice', 'Charlie'],
        'Listener': ['Bob', 'Alice', 'Charlie', 'Alice'],
        'text': ['Hello', 'Hi', 'Come in', 'Thanks'],
    })
    positions = ('scene',)
    pairs = cg.prepare_data(dialogue, positions, source='Speaker', target='Listener', interaction='text')
    pairs = cg.calculate_weights(pairs, weight_func=lambda text: 1)
    tg = cg.TGraph(data=pairs, positions=positions, directed=True)

The weight function assigns one to each pair interaction. If you already have
numeric weights, pass their column name as ``weight=`` to ``prepare_data`` and skip
``calculate_weights``. Use ``('scene', 'line')`` instead for line-level steps.
Positions must be numeric and ordered coarsest first; display labels are separate.

2. Select a graph and analyze it
--------------------------------

``get_graph`` returns an ``igraph.Graph`` for the selected point::

    g = tg.get_graph((1,))
    assert g.vcount() == 2
    assert g.ecount() == 2  # Alice -> Bob and Bob -> Alice

    degree = cg.graph_degree_centrality(g, weighted=True)
    degree.insert(0, 'character', g.vs['name'])
    print(degree)

Static centrality rows follow vertex order. Temporal centralities add names and
time columns automatically::

    per_scene = cg.tgraph_degree_centrality(tg, accumulate=False, weighted=True)
    assert list(per_scene.columns) == [
        'scene', 'character', 'in_degree', 'out_degree', 'all_degree',
        'weighted_in_degree', 'weighted_out_degree', 'weighted_all_degree',
    ]
    per_scene.to_csv('degrees.csv', index=False)

For raw interaction tables, temporal graph analyses default to cumulative history;
memory-state tables default to snapshots. Choose explicitly when comparing results::

    cumulative = cg.tgraph_degree_centrality(tg)  # all history through each step
    snapshots = cg.tgraph_degree_centrality(tg, accumulate=False)
    windowed = cg.tgraph_degree_centrality(tg, window_size=2)

A window counts observed steps, not seconds or line-number distance. Here a
two-step window includes the current and previous observed scenes.

3. Save or explore a view
-------------------------

Save a static HTML view without opening a browser::

    path = cg.graph_viz(g, output_file='scene-1.html', open_browser=False)

Open the file to explore it. The graph viewer loads its web libraries from a CDN,
so it needs internet access. To explore the full timeline interactively, run::

    cg.tgraph_viz(tg)

This opens a browser and keeps the terminal running until Ctrl+C. In a notebook,
use ``blocking=False`` and retain the returned server so you can close it later.
See :doc:`visualization` for cleanup, time labels and animation export.

4. Preserve group events with a hypergraph
------------------------------------------

When Alice addresses Bob and Charlie together, pair expansion produces two rows.
Hypergraph preparation keeps that utterance as one event::

    group_dialogue = pd.DataFrame({
        'scene': [1, 1, 2],
        'source': ['Alice', 'Alice', 'Bob'],
        'target': ['Bob, Charlie', 'Bob, Charlie', 'Charlie'],
    })
    events = cg.prepare_hypergraph_data(group_dialogue, positions=['scene'])
    th = cg.THypergraph(data=events, positions=['scene'])
    h = th.get_hypergraph((1,))
    assert h.ecount() == 2  # two utterances, even though the groups are identical
    assert h.vcount() == 3

    degree = cg.hypergraph_degree_centrality(h, include_character=True)
    print(degree)  # event participation, not pair degree
    cg.thypergraph_viz(th, output_file='groups-over-time.html', open_browser=False)

``THypergraph`` is directed by default, like ``TGraph``. Set ``directed=False`` on
both hypergraph preparation and construction to analyze undirected participation.
Hypergraph HTML exports are self-contained. See :doc:`hypergraph` for metric
definitions and :doc:`hypergraph_backends` for native research methods.

Next steps
----------

- :doc:`data`: load your CSV and choose the weight definition.
- :doc:`graph`: select hierarchical time points and windows.
- :doc:`analysis`: choose metrics, community models and time-respecting paths.
- :doc:`visualization`: customize viewers and export GIF/MP4.

The repository's ``ciga/examples/`` scripts use the tracked dialogue CSVs and should
be run from the checkout root after installation. Listener inference additionally
needs a configured model client. For a graph/hypergraph comparison using both CSVs,
run ``python examples/hypergraph_dialogue.py``; see :doc:`hypergraph` for its outputs.
