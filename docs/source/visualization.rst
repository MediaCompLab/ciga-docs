Visualization
=============

Choose a viewer for exploration or a file format for sharing. The examples below
continue with ``tg`` and ``g`` from :doc:`tutorials`.

.. contents:: On this page
   :local:
   :depth: 1

Choose an output
----------------

.. list-table:: Viewers and exports
   :header-rows: 1
   :widths: 35 40 25

   * - Function
     - Output / default behavior
     - Python extras
   * - ``graph_viz``
     - Static graph HTML file; opens a browser by default.
     - None
   * - ``tgraph_viz``
     - Local timeline server; opens a browser and blocks by default.
     - None
   * - ``hypergraph_viz``
     - Group-region HTML, PNG, SVG or PDF; HTML is the default.
     - None
   * - ``thypergraph_viz``
     - Local timeline server, or standalone HTML with ``output_file=``.
     - None
   * - ``tgraph_gif`` / ``tgraph_video``
     - GIF / MP4 animation file.
     - ``visualization``

Graph HTML viewers load vis-network from a CDN and need internet access for that
library. Hypergraph HTML exports embed their JavaScript and work offline. See
:doc:`hypergraph` for exact group membership, directed roles and geometry semantics.

Signed graphs preserve the classic straight edge style. Numeric labels are green
for positive values and red for negative values; signs remain visible. Each
direction of a bidirectional label is colored independently. SVG, GIF and MP4
retain the same convention. See :doc:`signed_weights` for decomposition, layout,
parallel-edge label and animation semantics.

Files and local servers
-----------------------

For a file without an automatic browser launch::

    path = cg.graph_viz(g, output_file='graph.html', open_browser=False)

``tgraph_viz(tg)`` opens a local explorer on port 8050 and blocks until Ctrl+C.
Raw graphs initially display cumulative history; memory-state graphs initially display
snapshots. The viewer offers cumulative, snapshot and delta modes for either input.
For a notebook or another nonblocking workflow::

    server = cg.tgraph_viz(tg, port=8050, blocking=False, open_browser=False)

Visit ``http://localhost:8050`` while the Python process is running. When finished::

    server.shutdown()
    server.server_close()

Nonblocking server modes return ``HTTPServer``. The blocking ``tgraph_viz`` call
returns ``None`` after shutdown. ``graph_viz(..., port=8050)`` also starts a
background server. Choose another port if one is already in use.

Hypergraph exports use ``hypergraph_viz(h, output_file='groups.html', open_browser=False)``
or ``thypergraph_viz(th, output_file='timeline.html', open_browser=False)`` and return
absolute path strings. A temporal hypergraph export defaults to cumulative frames;
pass ``accumulate=False`` for independent snapshots. Only the hypergraph temporal
viewer supports standalone timeline export; ``tgraph_viz`` requires its live server.

Human-readable time labels
--------------------------

Continue with ``tg`` from :doc:`tutorials`. The viewer and animation titles can
show text labels while keeping numeric positions for analysis::

    import pandas as pd

    labels = pd.DataFrame({
        "scene": [1, 2],
        "timestamp": ["Scene one", "Scene two"],
    })
    server = cg.tgraph_viz(
        tg, time_mapping=labels, time_label_column="timestamp", blocking=False
    )
    cg.tgraph_gif(
        tg,
        "dated.gif",
        time_mapping=labels,
        time_label_column="timestamp",
    )

Close ``server`` when finished, as shown above. Every position column must be present in a DataFrame mapping. Missing labels fall back
to numeric positions by default; set ``time_mapping_strict=True`` to require complete
coverage. The mapping never changes temporal ordering, windows, caching, or analysis.

GIF export
----------

The default GIF behavior renders every observed position without a frame cap. For large
graphs, ``frame_step`` and ``max_frames`` can be used independently or together::

    import ciga as cg

    cg.tgraph_gif(tg, "all_positions.gif")
    cg.tgraph_gif(
        tg,
        "sampled.gif",
        frame_step=5,
        max_frames=200,
        fps=12,
        mode="accumulate",
    )

The command-line entry point accepts a trusted local TGraph pickle::

    ciga-tgraph-gif tg.pkl animation.gif
    ciga-tgraph-gif tg.pkl sampled.gif --frame-step 5 --max-frames 200

Omitting ``--max-frames`` (or passing ``0``) leaves the frame count unlimited. Existing
files are not replaced unless ``--overwrite`` is provided. Run
``ciga-tgraph-gif --help`` for snapshot, window, interval, node, layout, colormap, and
canvas controls. CJK-capable fonts are auto-detected when available; use
``--font-family "Microsoft YaHei"`` (or another installed family) to override the
selection.

MP4 export
----------

MP4 export streams frames to FFmpeg. The example below uses the tutorial's scene
index. For positions measured in seconds, ``position_interval=3600`` instead samples
about hourly::

    cg.tgraph_video(
        tg,
        "timecourse.mp4",
        position_interval=1,
        fps=30,
        label_mode="none",
        crf=20,
        preset="medium",
    )

The default ``intensity_normalization="global"`` uses a common node and edge scale
for every frame, preserving absolute comparison over time. For memory-state snapshots,
the maxima are taken across the selected snapshots; for the ordinary cumulative mode
they come from the final accumulated graph. Use per-frame
relative intensity when early differences would otherwise be compressed::

    cg.tgraph_video(
        tg,
        "relative-timecourse.mp4",
        intensity_normalization="frame",
        element_scale=1.5,
        label_fontsize=7.0,
        node_size_range=(180.0, 420.0),
        edge_width_range=(0.4, 4.0),
    )

``element_scale`` multiplies node diameters, edge widths, labels, and titles without
changing the requested output pixel dimensions. The explicit size ranges remain in
Matplotlib point units. The command-line equivalents are
``--intensity-normalization frame``, ``--element-scale``, ``--label-fontsize``,
``--node-size-min``/``--node-size-max``, and
``--edge-width-min``/``--edge-width-max``.

``position_interval`` samples numeric position values by distance and always retains the
last position. ``label_mode`` may be ``all``, ``active``, or ``none``. Existing files are
not replaced unless ``overwrite=True`` is passed. GIF remains available for short previews.

``node_mode`` controls when a node enters the animation. The default ``active`` draws a
node only from the frame it takes part in an interaction: under ``mode='accumulate'`` the
cast grows and nodes stay once revealed, while ``mode='snapshot'`` and ``mode='window'``
show only the nodes interacting within that frame. ``node_mode='all'`` restores the earlier
behavior, where every node is drawn from the first frame and the ones that have not yet
interacted appear as grey placeholders. Either way the view is framed on the full layout,
so node positions do not shift as the cast appears. The command-line equivalent is
``--node-mode``.
API reference
-------------

.. currentmodule:: ciga

.. autofunction:: graph_viz
.. autofunction:: tgraph_viz
.. autofunction:: tgraph_gif
.. autofunction:: tgraph_video
