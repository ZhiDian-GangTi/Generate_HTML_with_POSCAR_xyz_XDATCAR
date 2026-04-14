# Structure HTML Tools

Small Python utilities for turning crystal structures and VASP trajectories into self-contained interactive HTML viewers.

- `scripts/cif_to_html.py`
  Converts a single crystal structure into an interactive HTML viewer with atom labels and adjustable supercell controls.
- `scripts/xdatcar_to_html.py`
  Detects single-frame vs multi-frame structure content automatically. Single-frame inputs become static HTML; multi-frame inputs become animated HTML with playback controls and an element legend.

The generated HTML files are self-contained and can be opened directly in a browser, shared with collaborators, or linked from presentation slides.

## Features

- Supports `CIF`, `POSCAR`, `CONTCAR`, `VASP`, `XYZ`, and `XDATCAR`-style data.
- Works offline after generation.
- Uses VESTA-style element colors for better readability.
- Mobile-friendly HTML layout.
- Single-structure viewer supports atom labels and arbitrary supercell expansion.
- Trajectory viewer supports animation controls, frame slider, FPS control, and a foldable legend.
- No third-party Python packages required.

## Repository Layout

```text
structure-html-tools/
|- scripts/
|  |- cif_to_html.py
|  `- xdatcar_to_html.py
|- vendor/
|  |- 3Dmol-min.js
|  `- 3Dmol-min.js.LICENSE.txt
|- examples/
|  |- static/
|  |  `- CONTCAR.cif
|  `- trajectory/
|     `- XDATCAR
|- .gitignore
|- LICENSE
|- README.md
`- THIRD_PARTY_NOTICES.md
```

## Requirements

- Python `3.10+`

## Quick Start

Clone the repository, then run one of the scripts from the repository root:

```powershell
python .\scripts\cif_to_html.py .\examples\static\CONTCAR.cif
python .\scripts\xdatcar_to_html.py .\examples\trajectory\XDATCAR
```

This creates HTML files next to the input files by default.

## Script 1: `cif_to_html.py`

Best for a single structure that you want to inspect, rotate, label, and expand as a supercell.

### Supported Input

- `.cif`
- `POSCAR`
- `CONTCAR`
- `.vasp`
- `.xyz`

### Example

```powershell
python .\scripts\cif_to_html.py .\examples\static\CONTCAR.cif
python .\scripts\cif_to_html.py .\examples\static\CONTCAR.cif --supercell 2 2 1
python .\scripts\cif_to_html.py .\examples\static\CONTCAR.cif -o .\examples\static\CONTCAR_viewer.html
```

### Output Behavior

- Displays atom labels directly on the structure.
- Uses VESTA-style element colors.
- Lets the viewer change the supercell interactively in the generated HTML.

## Script 2: `xdatcar_to_html.py`

Best for trajectories or folders containing mixed structure files when you want automatic single-frame vs multi-frame handling.

### Supported Input by Content

- XYZ with one or multiple frames
- VASP/XDATCAR-style files with one or multiple frames

The script does not rely only on the filename. It inspects file content and decides whether to build:

- a static HTML viewer for one frame
- an animated HTML viewer for multiple frames

### Example

```powershell
python .\scripts\xdatcar_to_html.py .\examples\trajectory\XDATCAR
python .\scripts\xdatcar_to_html.py .\examples\trajectory\XDATCAR --stride 5 --fps 12
python .\scripts\xdatcar_to_html.py
```

### Output Behavior

- Multi-frame inputs get animation playback controls.
- Single-frame inputs get a lightweight static viewer.
- The legend only shows elements that appear in the current structure.
- The legend is larger, foldable, and placed below the main control panel for presentation use.

## Typical Use Cases

- Prepare interactive crystal viewers for group meetings or class presentations.
- Share VASP trajectories without requiring specialized desktop visualization software.
- Generate browser-friendly structure pages that can be opened on phones or tablets.
- Create structure snapshots and then link the HTML from PowerPoint.

## Notes

- The generated HTML is self-contained, but the Python scripts still need `vendor/3Dmol-min.js` when generating new files.
- Output `.html` files and `__pycache__` are ignored by default in `.gitignore`.
- If you want to publish the generated viewers separately, commit the HTML files in another repo or release artifact folder instead of this source repo.

## License

The Python scripts and repository materials in this project are released under the [MIT License](LICENSE).

This repository also bundles `3Dmol-min.js`, which remains under its own upstream license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [vendor/3Dmol-min.js.LICENSE.txt](vendor/3Dmol-min.js.LICENSE.txt).
