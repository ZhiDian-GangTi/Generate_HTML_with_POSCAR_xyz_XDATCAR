#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path


ELEMENT_RE = re.compile(r"[A-Za-z]{1,2}")
INT_RE = re.compile(r"^[+-]?\d+$")
SKIP_SUFFIXES = {
    ".html",
    ".py",
    ".js",
    ".css",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".pdf",
    ".zip",
    ".7z",
    ".rar",
}

ELEMENT_NAMES_EN = {
    "H": "Hydrogen",
    "He": "Helium",
    "Li": "Lithium",
    "Be": "Beryllium",
    "B": "Boron",
    "C": "Carbon",
    "N": "Nitrogen",
    "O": "Oxygen",
    "F": "Fluorine",
    "Ne": "Neon",
    "Na": "Sodium",
    "Mg": "Magnesium",
    "Al": "Aluminum",
    "Si": "Silicon",
    "P": "Phosphorus",
    "S": "Sulfur",
    "Cl": "Chlorine",
    "Ar": "Argon",
    "K": "Potassium",
    "Ca": "Calcium",
    "Sc": "Scandium",
    "Ti": "Titanium",
    "V": "Vanadium",
    "Cr": "Chromium",
    "Mn": "Manganese",
    "Fe": "Iron",
    "Co": "Cobalt",
    "Ni": "Nickel",
    "Cu": "Copper",
    "Zn": "Zinc",
    "Ga": "Gallium",
    "Ge": "Germanium",
    "As": "Arsenic",
    "Se": "Selenium",
    "Br": "Bromine",
    "Kr": "Krypton",
    "Rb": "Rubidium",
    "Sr": "Strontium",
    "Y": "Yttrium",
    "Zr": "Zirconium",
    "Nb": "Niobium",
    "Mo": "Molybdenum",
    "Tc": "Technetium",
    "Ru": "Ruthenium",
    "Rh": "Rhodium",
    "Pd": "Palladium",
    "Ag": "Silver",
    "Cd": "Cadmium",
    "In": "Indium",
    "Sn": "Tin",
    "Sb": "Antimony",
    "Te": "Tellurium",
    "I": "Iodine",
    "Xe": "Xenon",
    "Cs": "Cesium",
    "Ba": "Barium",
    "La": "Lanthanum",
    "Ce": "Cerium",
    "Pr": "Praseodymium",
    "Nd": "Neodymium",
    "Pm": "Promethium",
    "Sm": "Samarium",
    "Eu": "Europium",
    "Gd": "Gadolinium",
    "Tb": "Terbium",
    "Dy": "Dysprosium",
    "Ho": "Holmium",
    "Er": "Erbium",
    "Tm": "Thulium",
    "Yb": "Ytterbium",
    "Lu": "Lutetium",
    "Hf": "Hafnium",
    "Ta": "Tantalum",
    "W": "Tungsten",
    "Re": "Rhenium",
    "Os": "Osmium",
    "Ir": "Iridium",
    "Pt": "Platinum",
    "Au": "Gold",
    "Hg": "Mercury",
    "Tl": "Thallium",
    "Pb": "Lead",
    "Bi": "Bismuth",
    "Po": "Polonium",
    "At": "Astatine",
    "Rn": "Radon",
    "Fr": "Francium",
    "Ra": "Radium",
    "Ac": "Actinium",
    "Th": "Thorium",
    "Pa": "Protactinium",
    "U": "Uranium",
    "Np": "Neptunium",
    "Pu": "Plutonium",
    "Am": "Americium",
    "Cm": "Curium",
    "Bk": "Berkelium",
    "Cf": "Californium",
    "Es": "Einsteinium",
    "Fm": "Fermium",
    "Md": "Mendelevium",
    "No": "Nobelium",
    "Lr": "Lawrencium",
    "Rf": "Rutherfordium",
    "Db": "Dubnium",
    "Sg": "Seaborgium",
    "Bh": "Bohrium",
    "Hs": "Hassium",
    "Mt": "Meitnerium",
}

VESTA_COLORS = {
    "H": "#ffcccc",
    "He": "#fce8ce",
    "Li": "#86df73",
    "Be": "#5ed77b",
    "B": "#1fa20f",
    "C": "#4c4c4c",
    "N": "#b0b9e6",
    "O": "#fe0300",
    "F": "#b0b9e6",
    "Ne": "#fe37b5",
    "Na": "#f9dc3c",
    "Mg": "#fb7b15",
    "Al": "#81b2d6",
    "Si": "#1b3bfa",
    "P": "#c09cc2",
    "S": "#fffa00",
    "Cl": "#31fc02",
    "Ar": "#cffec4",
    "K": "#a121f6",
    "Ca": "#5a96bd",
    "Sc": "#b563ab",
    "Ti": "#78caff",
    "V": "#e51900",
    "Cr": "#00009e",
    "Mn": "#a7089d",
    "Fe": "#b57100",
    "Co": "#0000af",
    "Ni": "#b7bbbd",
    "Cu": "#2247dc",
    "Zn": "#8f8f81",
    "Ga": "#9ee373",
    "Ge": "#7e6ea6",
    "As": "#74d057",
    "Se": "#9aef0f",
    "Br": "#7e3102",
    "Kr": "#fac1f3",
    "Rb": "#702eb0",
    "Sr": "#00ff00",
    "Y": "#94ffff",
    "Zr": "#00ff00",
    "Nb": "#73c2c9",
    "Mo": "#54b5b5",
    "Tc": "#3b9e9e",
    "Ru": "#248f8f",
    "Rh": "#0a7d8c",
    "Pd": "#006985",
    "Ag": "#c0c0c0",
    "Cd": "#ffd98f",
    "In": "#a67573",
    "Sn": "#9a8eb9",
    "Sb": "#9e63b5",
    "Te": "#d47a00",
    "I": "#940094",
    "Xe": "#429eb0",
    "Cs": "#57178f",
    "Ba": "#00c900",
    "La": "#5ac449",
    "Ce": "#ffffc7",
    "Pr": "#d9ffc7",
    "Nd": "#c7ffc7",
    "Pm": "#a3ffc7",
    "Sm": "#8fffc7",
    "Eu": "#61ffc7",
    "Gd": "#45ffc7",
    "Tb": "#30ffc7",
    "Dy": "#1fffc7",
    "Ho": "#00ff9c",
    "Er": "#00e675",
    "Tm": "#00d452",
    "Yb": "#00bf38",
    "Lu": "#00ab24",
    "Hf": "#4dc2ff",
    "Ta": "#4da6ff",
    "W": "#2194d6",
    "Re": "#267dab",
    "Os": "#266696",
    "Ir": "#175487",
    "Pt": "#d0d0e0",
    "Au": "#ffd123",
    "Hg": "#b8b8d0",
    "Tl": "#a6544d",
    "Pb": "#575961",
    "Bi": "#9e4fb5",
    "Po": "#ab5c00",
    "At": "#754f45",
    "Rn": "#428296",
    "Fr": "#420066",
    "Ra": "#007d00",
    "Ac": "#70abfa",
    "Th": "#00baff",
    "Pa": "#00a1ff",
    "U": "#008fff",
    "Np": "#0080ff",
    "Pu": "#006bff",
    "Am": "#545cf2",
    "Cm": "#785ce3",
    "Bk": "#8a4fe3",
    "Cf": "#a136d4",
    "Es": "#b31fd4",
    "Fm": "#b31fba",
    "Md": "#b30da6",
    "No": "#bd0d87",
    "Lr": "#c70066",
    "Rf": "#cc0059",
    "Db": "#d1004f",
    "Sg": "#d90045",
    "Bh": "#e00038",
    "Hs": "#e6002e",
    "Mt": "#eb0026",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Auto-detect structure files by content. "
            "Single-frame files become static HTML; multi-frame files become animated HTML."
        )
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help=(
            "Path to one structure file. If omitted, the script scans the current working directory "
            "and the script directory, then converts every parseable structure file it finds."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML path for single-file conversion. Ignored in batch mode.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Keep every Nth frame to reduce HTML size and speed up playback. Default: 1",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=8.0,
        help="Default playback speed in frames per second. Default: 8",
    )
    return parser.parse_args()


def is_int_token(token: str) -> bool:
    return bool(INT_RE.fullmatch(token.strip()))


def normalize_element(raw_symbol: str | None, label: str) -> str:
    for candidate in (raw_symbol, label):
        if not candidate or candidate in {"?", "."}:
            continue
        match = ELEMENT_RE.search(candidate)
        if match:
            symbol = match.group(0)
            return symbol[0].upper() + symbol[1:].lower()
    return "X"


def parse_float_triplet(line: str) -> list[float]:
    tokens = line.split()
    if len(tokens) < 3:
        raise ValueError(f"Expected at least three numeric values, got: {line!r}")
    return [float(tokens[0]), float(tokens[1]), float(tokens[2])]


def dot(vec1: list[float], vec2: list[float]) -> float:
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]


def cross(vec1: list[float], vec2: list[float]) -> list[float]:
    return [
        vec1[1] * vec2[2] - vec1[2] * vec2[1],
        vec1[2] * vec2[0] - vec1[0] * vec2[2],
        vec1[0] * vec2[1] - vec1[1] * vec2[0],
    ]


def vector_length(vector: list[float]) -> float:
    return math.sqrt(dot(vector, vector))


def determinant_from_vectors(a_vec: list[float], b_vec: list[float], c_vec: list[float]) -> float:
    return dot(a_vec, cross(b_vec, c_vec))


def scale_lattice_vectors(scale_tokens: list[str], raw_vectors: list[list[float]]) -> tuple[list[list[float]], float]:
    if len(scale_tokens) == 1:
        scale_value = float(scale_tokens[0])
        if scale_value < 0:
            raw_volume = abs(determinant_from_vectors(*raw_vectors))
            if raw_volume <= 0:
                raise ValueError("XDATCAR lattice volume must be positive")
            scale_factor = (abs(scale_value) / raw_volume) ** (1.0 / 3.0)
        else:
            scale_factor = scale_value
        return (
            [[component * scale_factor for component in vector] for vector in raw_vectors],
            scale_factor,
        )

    if len(scale_tokens) == 3:
        scale_factors = [float(token) for token in scale_tokens]
        vectors = [
            [raw_vectors[row][col] * scale_factors[col] for col in range(3)]
            for row in range(3)
        ]
        return vectors, 1.0

    raise ValueError("XDATCAR scale line must contain one or three numbers")


def frac_to_cart(frac: list[float], vectors: list[list[float]]) -> list[float]:
    return [
        frac[0] * vectors[0][0] + frac[1] * vectors[1][0] + frac[2] * vectors[2][0],
        frac[0] * vectors[0][1] + frac[1] * vectors[1][1] + frac[2] * vectors[2][1],
        frac[0] * vectors[0][2] + frac[1] * vectors[1][2] + frac[2] * vectors[2][2],
    ]


def build_labels(elements: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    labels: list[str] = []
    for elem in elements:
        counts[elem] = counts.get(elem, 0) + 1
        labels.append(f"{elem}{counts[elem]}")
    return labels


def build_bounding_vectors(frames: list[list[list[float]]]) -> list[list[float]]:
    xs = [coord[0] for frame in frames for coord in frame]
    ys = [coord[1] for frame in frames for coord in frame]
    zs = [coord[2] for frame in frames for coord in frame]
    padding = 2.0
    lengths = [
        max(max(xs) - min(xs) + 2 * padding, 5.0),
        max(max(ys) - min(ys) + 2 * padding, 5.0),
        max(max(zs) - min(zs) + 2 * padding, 5.0),
    ]
    return [
        [lengths[0], 0.0, 0.0],
        [0.0, lengths[1], 0.0],
        [0.0, 0.0, lengths[2]],
    ]


def parse_xyz_frames(path: Path, stride: int) -> dict:
    if stride < 1:
        raise ValueError("Stride must be a positive integer")

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    index = 0
    frames: list[list[list[float]]] = []
    elements: list[str] | None = None
    title = path.stem

    while True:
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines):
            break

        header = lines[index].strip()
        if not is_int_token(header):
            raise ValueError("XYZ frame header must be an integer atom count")

        atom_count = int(header)
        if atom_count <= 0:
            raise ValueError("XYZ atom count must be positive")
        if index + 1 >= len(lines):
            raise ValueError("XYZ file ended before the comment line")

        comment = lines[index + 1].strip()
        if comment and not frames:
            title = comment

        frame_elements: list[str] = []
        frame_coords: list[list[float]] = []
        index += 2

        for _ in range(atom_count):
            if index >= len(lines):
                raise ValueError("XYZ file ended in the middle of a frame")
            tokens = lines[index].split()
            if len(tokens) < 4:
                raise ValueError(f"Invalid XYZ atom line: {lines[index]!r}")
            frame_elements.append(normalize_element(tokens[0], tokens[0]))
            frame_coords.append([float(tokens[1]), float(tokens[2]), float(tokens[3])])
            index += 1

        if elements is None:
            elements = frame_elements
        elif frame_elements != elements:
            raise ValueError("XYZ frames do not keep a consistent atom ordering")

        frames.append(frame_coords)

    if not frames or elements is None:
        raise ValueError("No XYZ frames were found")

    kept_frames = frames[::stride]
    if kept_frames[-1] is not frames[-1]:
        kept_frames.append(frames[-1])

    return {
        "title": title,
        "vectors": build_bounding_vectors(frames),
        "elements": elements,
        "labels": build_labels(elements),
        "frames": kept_frames,
        "raw_frame_count": len(frames),
        "atom_count": len(elements),
        "stride": stride,
        "show_unit_cell": False,
        "source_format": "xyz",
    }


def iter_candidate_files(search_dirs: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    candidates: list[Path] = []

    for directory in search_dirs:
        if not directory.exists() or not directory.is_dir():
            continue
        for path in sorted(directory.iterdir(), key=lambda candidate: candidate.name.lower()):
            if not path.is_file():
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            if path.name.lower() == "3dmol-min.js":
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(resolved)

    return candidates


def parse_xdatcar(path: Path, stride: int) -> dict:
    if stride < 1:
        raise ValueError("Stride must be a positive integer")

    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    if len(lines) < 8:
        raise ValueError("XDATCAR file is too short")

    title = lines[0] or path.stem
    scale_tokens = lines[1].split()
    raw_vectors = [parse_float_triplet(lines[2]), parse_float_triplet(lines[3]), parse_float_triplet(lines[4])]
    vectors, coord_scale = scale_lattice_vectors(scale_tokens, raw_vectors)

    species_tokens = lines[5].split()
    count_tokens = lines[6].split()
    if not species_tokens or not count_tokens or not all(is_int_token(token) for token in count_tokens):
        raise ValueError("Could not parse XDATCAR species/count header")

    species = [normalize_element(token, token) for token in species_tokens]
    counts = [int(token) for token in count_tokens]
    if len(species) != len(counts):
        raise ValueError("XDATCAR species line and counts line have different lengths")

    elements = [species[idx] for idx, count in enumerate(counts) for _ in range(count)]
    atom_count = len(elements)
    labels = build_labels(elements)

    frames: list[list[list[float]]] = []
    line_index = 7
    while line_index < len(lines):
        header = lines[line_index]
        header_lower = header.lower()
        if header_lower.startswith("direct") or header_lower.startswith("cart"):
            direct_mode = header_lower.startswith("direct")
            frame_cart: list[list[float]] = []
            for offset in range(atom_count):
                coord_line_index = line_index + 1 + offset
                if coord_line_index >= len(lines):
                    raise ValueError("XDATCAR ended in the middle of a frame")
                coords = parse_float_triplet(lines[coord_line_index])
                if direct_mode:
                    cart = frac_to_cart(coords, vectors)
                else:
                    cart = [coords[0] * coord_scale, coords[1] * coord_scale, coords[2] * coord_scale]
                frame_cart.append(cart)
            frames.append(frame_cart)
            line_index += atom_count + 1
            continue

        raise ValueError(f"Unexpected XDATCAR frame header: {header!r}")

    if not frames:
        raise ValueError("No trajectory frames were found in XDATCAR")

    kept_frames = frames[::stride]
    if kept_frames[-1] is not frames[-1]:
        kept_frames.append(frames[-1])

    return {
        "title": title,
        "vectors": vectors,
        "elements": elements,
        "labels": labels,
        "frames": kept_frames,
        "raw_frame_count": len(frames),
        "atom_count": atom_count,
        "stride": stride,
        "show_unit_cell": True,
        "source_format": "vasp",
    }


def parse_structure_by_content(path: Path, stride: int) -> dict:
    parse_errors: list[str] = []

    for parser in (parse_xyz_frames, parse_xdatcar):
        try:
            return parser(path, stride)
        except Exception as exc:
            parse_errors.append(f"{parser.__name__}: {exc}")

    joined = "; ".join(parse_errors)
    raise ValueError(f"Could not recognize {path.name!r} as a supported structure file. {joined}")


def discover_parseable_structures(search_dirs: list[Path], stride: int) -> list[tuple[Path, dict]]:
    matches: list[tuple[Path, dict]] = []
    for path in iter_candidate_files(search_dirs):
        try:
            structure = parse_structure_by_content(path, stride)
        except Exception:
            continue
        matches.append((path, structure))
    return matches


def build_xyz_multiframe(elements: list[str], frames: list[list[list[float]]]) -> str:
    atom_count = len(elements)
    blocks: list[str] = []
    for frame_index, frame in enumerate(frames, start=1):
        lines = [str(atom_count), f"Frame {frame_index}"]
        for elem, position in zip(elements, frame, strict=True):
            lines.append(f"{elem} {position[0]:.6f} {position[1]:.6f} {position[2]:.6f}")
        blocks.append("\n".join(lines))
    return "\n".join(blocks)


def build_xyz_singleframe(elements: list[str], frame: list[list[float]], title: str) -> str:
    lines = [str(len(elements)), title]
    for elem, position in zip(elements, frame, strict=True):
        lines.append(f"{elem} {position[0]:.6f} {position[1]:.6f} {position[2]:.6f}")
    return "\n".join(lines)


def make_default_output_path(input_path: Path) -> Path:
    if input_path.suffix:
        return input_path.with_suffix(".html")
    return input_path.with_name(f"{input_path.name}.html")


def unique_elements(elements: list[str]) -> list[str]:
    return list(dict.fromkeys(elements))


def build_legend_html(elements: list[str]) -> str:
    items: list[str] = []
    for elem in unique_elements(elements):
        color = VESTA_COLORS.get(elem, "#9ca3af")
        name_en = ELEMENT_NAMES_EN.get(elem, elem)
        label_symbol = html.escape(elem)
        label_name = html.escape(name_en)
        items.append(
            '<span class="legend-item">'
            f'<span class="legend-swatch" style="background:{color};"></span>'
            '<span class="legend-text">'
            f'<span class="legend-symbol">{label_symbol}</span>'
            f'<span class="legend-name">{label_name}</span>'
            "</span>"
            "</span>"
        )
    return "\n    ".join(items)


def load_viewer_library() -> str:
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "3Dmol-min.js",
        script_dir.parent / "vendor" / "3Dmol-min.js",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8").replace("</script>", "<\\/script>")

    raise FileNotFoundError(
        "3Dmol-min.js was not found. Put it next to xdatcar_to_html.py or in ../vendor/3Dmol-min.js."
    )


def build_html(trajectory: dict, viewer_js: str, default_fps: float) -> str:
    xyz_data = build_xyz_multiframe(trajectory["elements"], trajectory["frames"])
    legend_html = build_legend_html(trajectory["elements"])
    elements = unique_elements(trajectory["elements"])
    payload = {
        "title": trajectory["title"],
        "frameCount": len(trajectory["frames"]),
        "rawFrameCount": trajectory["raw_frame_count"],
        "stride": trajectory["stride"],
        "atomCount": trajectory["atom_count"],
        "vectors": {
            "a": trajectory["vectors"][0],
            "b": trajectory["vectors"][1],
            "c": trajectory["vectors"][2],
        },
        "elements": elements,
        "defaultFps": max(0.5, default_fps),
        "showUnitCell": trajectory["show_unit_cell"],
        "sourceFormat": trajectory["source_format"],
    }

    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    colors_json = json.dumps(VESTA_COLORS, ensure_ascii=False, indent=2)
    xyz_json = json.dumps(xyz_data, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{trajectory["title"]} Trajectory</title>
  <style>
    html, body {{
      width: 100%;
      height: 100%;
      margin: 0;
      background: #ffffff;
      overflow: hidden;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}

    #viewer {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      touch-action: none;
    }}

    #panel {{
      position: fixed;
      top: 16px;
      left: 16px;
      right: 16px;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      max-width: 620px;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.96);
      border: 1px solid #d1d5db;
      border-radius: 12px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.14);
      color: #111827;
      font-size: 13px;
      backdrop-filter: blur(8px);
      touch-action: manipulation;
    }}

    #legend {{
      position: fixed;
      left: 16px;
      z-index: 10;
      width: min(460px, calc(100vw - 32px));
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid #d1d5db;
      border-radius: 12px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
      color: #111827;
      font-size: 15px;
      backdrop-filter: blur(8px);
    }}

    .legend-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .legend-title {{
      font-size: 16px;
      font-weight: 700;
    }}

    #legend-toggle {{
      padding: 7px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 999px;
      background: #ffffff;
      color: #0f172a;
      font: inherit;
      cursor: pointer;
    }}

    #legend.collapsed .legend-header {{
      margin-bottom: 0;
    }}

    #legend.collapsed #legend-body {{
      display: none;
    }}

    #legend-body {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px 18px;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
      min-width: 180px;
    }}

    .legend-swatch {{
      width: 18px;
      height: 18px;
      border: 1px solid rgba(15, 23, 42, 0.25);
      border-radius: 999px;
      flex: 0 0 auto;
    }}

    .legend-text {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      line-height: 1.15;
    }}

    .legend-symbol {{
      font-size: 16px;
      font-weight: 700;
      color: #0f172a;
    }}

    .legend-name {{
      font-size: 14px;
      color: #475569;
    }}

    #title {{
      font-weight: 600;
      margin-right: 6px;
    }}

    #frame-slider {{
      width: min(260px, 45vw);
    }}

    #panel button,
    #panel input {{
      font: inherit;
    }}

    #panel button {{
      padding: 6px 12px;
      border: 1px solid #0f172a;
      border-radius: 8px;
      background: #0f172a;
      color: #ffffff;
      cursor: pointer;
    }}

    #panel button.secondary {{
      background: #ffffff;
      color: #0f172a;
    }}

    #panel input[type="number"] {{
      width: 68px;
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      background: #ffffff;
      color: #111827;
    }}

    #meta {{
      color: #475569;
    }}

    @media (max-width: 720px) {{
      #panel {{
        top: 12px;
        left: 12px;
        right: 12px;
        max-width: none;
        padding: 10px 12px;
      }}

      #frame-slider {{
        width: 100%;
      }}

      #legend {{
        left: 12px;
        right: 12px;
        width: auto;
        padding: 10px 12px;
      }}

      .legend-item {{
        min-width: 0;
      }}
    }}
  </style>
</head>
<body>
  <div id="viewer"></div>

  <div id="panel">
    <span id="title">{trajectory["title"]}</span>
    <button id="prev-button" class="secondary" type="button">Prev</button>
    <button id="play-button" type="button">Play</button>
    <button id="next-button" class="secondary" type="button">Next</button>
    <input id="frame-slider" type="range" min="1" max="{len(trajectory["frames"])}" value="1">
    <span id="frame-text">1 / {len(trajectory["frames"])}</span>
    <label for="fps-input">FPS</label>
    <input id="fps-input" type="number" min="0.5" max="60" step="0.5" value="{max(0.5, default_fps):.1f}">
    <span id="meta">{trajectory["atom_count"]} atoms, {len(trajectory["frames"])} frames</span>
  </div>

  <div id="legend">
    <div class="legend-header">
      <span class="legend-title">元素图例 / Legend</span>
      <button id="legend-toggle" type="button" aria-expanded="true">收起图例</button>
    </div>
    <div id="legend-body">
      {legend_html}
    </div>
  </div>

  <script>
{viewer_js}
  </script>
  <script>
    const trajectory = {payload_json};
    const vestaColors = {colors_json};
    const xyzData = {xyz_json};

    const viewer = $3Dmol.createViewer("viewer", {{ backgroundColor: "white" }});
    const viewerElement = document.getElementById("viewer");
    const playButton = document.getElementById("play-button");
    const prevButton = document.getElementById("prev-button");
    const nextButton = document.getElementById("next-button");
    const frameSlider = document.getElementById("frame-slider");
    const frameText = document.getElementById("frame-text");
    const fpsInput = document.getElementById("fps-input");
    const meta = document.getElementById("meta");
    const panelElement = document.getElementById("panel");
    const legendElement = document.getElementById("legend");
    const legendToggle = document.getElementById("legend-toggle");

    const state = {{
      currentFrame: 0,
      playing: false,
      timer: null,
      requestId: 0,
    }};

    function scaleVector(vector, factor) {{
      return {{
        x: vector[0] * factor,
        y: vector[1] * factor,
        z: vector[2] * factor,
      }};
    }}

    function addVectors(...vectors) {{
      return vectors.reduce(
        (acc, vector) => ({{
          x: acc.x + vector.x,
          y: acc.y + vector.y,
          z: acc.z + vector.z,
        }}),
        {{ x: 0, y: 0, z: 0 }}
      );
    }}

    function drawUnitCell() {{
      const origin = {{ x: 0, y: 0, z: 0 }};
      const va = scaleVector(trajectory.vectors.a, 1);
      const vb = scaleVector(trajectory.vectors.b, 1);
      const vc = scaleVector(trajectory.vectors.c, 1);

      const p000 = origin;
      const p100 = addVectors(origin, va);
      const p010 = addVectors(origin, vb);
      const p001 = addVectors(origin, vc);
      const p110 = addVectors(origin, va, vb);
      const p101 = addVectors(origin, va, vc);
      const p011 = addVectors(origin, vb, vc);
      const p111 = addVectors(origin, va, vb, vc);

      const edges = [
        [p000, p100], [p000, p010], [p000, p001],
        [p100, p110], [p100, p101],
        [p010, p110], [p010, p011],
        [p001, p101], [p001, p011],
        [p110, p111], [p101, p111], [p011, p111],
      ];

      for (const [start, end] of edges) {{
        viewer.addLine({{
          start,
          end,
          color: "#475569",
          linewidth: 2,
        }});
      }}
    }}

    function applyElementStyles() {{
      for (const elem of trajectory.elements) {{
        const color = vestaColors[elem] ?? "#9ca3af";
        viewer.setStyle({{ elem }}, {{
          sphere: {{
            scale: 0.24,
            color,
          }},
          stick: {{
            radius: 0.12,
            color,
          }},
        }});
      }}
    }}

    function clampFrame(frameIndex) {{
      return Math.max(0, Math.min(trajectory.frameCount - 1, frameIndex));
    }}

    function positionLegend() {{
      const top = Math.round(panelElement.getBoundingClientRect().bottom + 12);
      legendElement.style.top = `${{top}}px`;
    }}

    function syncLegendToggle() {{
      const collapsed = legendElement.classList.contains("collapsed");
      legendToggle.textContent = collapsed ? "展开图例" : "收起图例";
      legendToggle.setAttribute("aria-expanded", String(!collapsed));
      positionLegend();
    }}

    function clearTimer() {{
      if (state.timer !== null) {{
        window.clearTimeout(state.timer);
        state.timer = null;
      }}
    }}

    function stopPlayback() {{
      state.playing = false;
      clearTimer();
      playButton.textContent = "Play";
    }}

    function getPlaybackInterval() {{
      const parsed = Number.parseFloat(fpsInput.value);
      const fps = Number.isFinite(parsed) ? Math.max(0.5, Math.min(60, parsed)) : trajectory.defaultFps;
      fpsInput.value = fps.toFixed(1);
      return 1000 / fps;
    }}

    async function showFrame(frameIndex) {{
      const nextFrame = clampFrame(frameIndex);
      state.currentFrame = nextFrame;
      frameSlider.value = String(nextFrame + 1);
      frameText.textContent = `${{nextFrame + 1}} / ${{trajectory.frameCount}}`;

      const requestId = ++state.requestId;
      await viewer.setFrame(nextFrame);
      if (requestId !== state.requestId) {{
        return;
      }}
      viewer.render();
    }}

    async function stepFrame(delta) {{
      stopPlayback();
      await showFrame(state.currentFrame + delta);
    }}

    async function tick() {{
      if (!state.playing) {{
        return;
      }}
      await showFrame((state.currentFrame + 1) % trajectory.frameCount);
      if (!state.playing) {{
        return;
      }}
      state.timer = window.setTimeout(tick, getPlaybackInterval());
    }}

    function startPlayback() {{
      if (state.playing || trajectory.frameCount <= 1) {{
        return;
      }}
      state.playing = true;
      playButton.textContent = "Pause";
      clearTimer();
      state.timer = window.setTimeout(tick, getPlaybackInterval());
    }}

    playButton.addEventListener("click", () => {{
      if (state.playing) {{
        stopPlayback();
      }} else {{
        startPlayback();
      }}
    }});

    prevButton.addEventListener("click", async () => {{
      await stepFrame(-1);
    }});

    nextButton.addEventListener("click", async () => {{
      await stepFrame(1);
    }});

    frameSlider.addEventListener("input", async (event) => {{
      stopPlayback();
      const value = Number.parseInt(event.target.value, 10);
      await showFrame((Number.isFinite(value) ? value : 1) - 1);
    }});

    fpsInput.addEventListener("change", () => {{
      if (state.playing) {{
        clearTimer();
        state.timer = window.setTimeout(tick, getPlaybackInterval());
      }} else {{
        getPlaybackInterval();
      }}
    }});

    legendToggle.addEventListener("click", () => {{
      legendElement.classList.toggle("collapsed");
      syncLegendToggle();
    }});

    viewerElement.addEventListener("pointerdown", () => {{
      clearTimer();
      if (state.playing) {{
        state.timer = window.setTimeout(tick, getPlaybackInterval());
      }}
    }}, {{ passive: true }});

    window.addEventListener("resize", () => {{
      viewer.resize();
      viewer.render();
      positionLegend();
    }});

    async function init() {{
      viewer.addModelsAsFrames(xyzData, "xyz");
      applyElementStyles();
      if (trajectory.showUnitCell) {{
        drawUnitCell();
      }}
      viewer.zoomTo();
      await showFrame(0);
      syncLegendToggle();
      meta.textContent = `${{trajectory.atomCount}} atoms, ${{trajectory.frameCount}} frames` +
        (trajectory.stride > 1 ? `, stride ${{trajectory.stride}} from ${{trajectory.rawFrameCount}}` : "");
    }}

    init();
  </script>
</body>
</html>
"""


def build_static_html(structure: dict, viewer_js: str) -> str:
    xyz_data = build_xyz_singleframe(structure["elements"], structure["frames"][0], structure["title"])
    legend_html = build_legend_html(structure["elements"])
    elements = unique_elements(structure["elements"])
    payload = {
        "title": structure["title"],
        "atomCount": structure["atom_count"],
        "vectors": {
            "a": structure["vectors"][0],
            "b": structure["vectors"][1],
            "c": structure["vectors"][2],
        },
        "elements": elements,
        "showUnitCell": structure["show_unit_cell"],
        "sourceFormat": structure["source_format"],
    }

    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    colors_json = json.dumps(VESTA_COLORS, ensure_ascii=False, indent=2)
    xyz_json = json.dumps(xyz_data, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{structure["title"]} Structure</title>
  <style>
    html, body {{
      width: 100%;
      height: 100%;
      margin: 0;
      background: #ffffff;
      overflow: hidden;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}

    #viewer {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      touch-action: none;
    }}

    #panel {{
      position: fixed;
      top: 16px;
      left: 16px;
      right: 16px;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      max-width: 520px;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.96);
      border: 1px solid #d1d5db;
      border-radius: 12px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.14);
      color: #111827;
      font-size: 13px;
      backdrop-filter: blur(8px);
      touch-action: manipulation;
    }}

    #legend {{
      position: fixed;
      left: 16px;
      z-index: 10;
      width: min(460px, calc(100vw - 32px));
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid #d1d5db;
      border-radius: 12px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
      color: #111827;
      font-size: 15px;
      backdrop-filter: blur(8px);
    }}

    .legend-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .legend-title {{
      font-size: 16px;
      font-weight: 700;
    }}

    #legend-toggle {{
      padding: 7px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 999px;
      background: #ffffff;
      color: #0f172a;
      font: inherit;
      cursor: pointer;
    }}

    #legend.collapsed .legend-header {{
      margin-bottom: 0;
    }}

    #legend.collapsed #legend-body {{
      display: none;
    }}

    #legend-body {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px 18px;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
      min-width: 180px;
    }}

    .legend-swatch {{
      width: 18px;
      height: 18px;
      border: 1px solid rgba(15, 23, 42, 0.25);
      border-radius: 999px;
      flex: 0 0 auto;
    }}

    .legend-text {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      line-height: 1.15;
    }}

    .legend-symbol {{
      font-size: 16px;
      font-weight: 700;
      color: #0f172a;
    }}

    .legend-name {{
      font-size: 14px;
      color: #475569;
    }}

    #title {{
      font-weight: 600;
      margin-right: 6px;
    }}

    #meta {{
      color: #475569;
    }}

    @media (max-width: 720px) {{
      #panel {{
        top: 12px;
        left: 12px;
        right: 12px;
        max-width: none;
        padding: 10px 12px;
      }}

      #legend {{
        left: 12px;
        right: 12px;
        width: auto;
        padding: 10px 12px;
      }}

      .legend-item {{
        min-width: 0;
      }}
    }}
  </style>
</head>
<body>
  <div id="viewer"></div>

  <div id="panel">
    <span id="title">{structure["title"]}</span>
    <span id="meta">{structure["atom_count"]} atoms</span>
  </div>

  <div id="legend">
    <div class="legend-header">
      <span class="legend-title">元素图例 / Legend</span>
      <button id="legend-toggle" type="button" aria-expanded="true">收起图例</button>
    </div>
    <div id="legend-body">
      {legend_html}
    </div>
  </div>

  <script>
{viewer_js}
  </script>
  <script>
    const structure = {payload_json};
    const vestaColors = {colors_json};
    const xyzData = {xyz_json};
    const viewer = $3Dmol.createViewer("viewer", {{ backgroundColor: "white" }});
    const panelElement = document.getElementById("panel");
    const legendElement = document.getElementById("legend");
    const legendToggle = document.getElementById("legend-toggle");

    function scaleVector(vector, factor) {{
      return {{
        x: vector[0] * factor,
        y: vector[1] * factor,
        z: vector[2] * factor,
      }};
    }}

    function addVectors(...vectors) {{
      return vectors.reduce(
        (acc, vector) => ({{
          x: acc.x + vector.x,
          y: acc.y + vector.y,
          z: acc.z + vector.z,
        }}),
        {{ x: 0, y: 0, z: 0 }}
      );
    }}

    function drawUnitCell() {{
      const origin = {{ x: 0, y: 0, z: 0 }};
      const va = scaleVector(structure.vectors.a, 1);
      const vb = scaleVector(structure.vectors.b, 1);
      const vc = scaleVector(structure.vectors.c, 1);

      const p000 = origin;
      const p100 = addVectors(origin, va);
      const p010 = addVectors(origin, vb);
      const p001 = addVectors(origin, vc);
      const p110 = addVectors(origin, va, vb);
      const p101 = addVectors(origin, va, vc);
      const p011 = addVectors(origin, vb, vc);
      const p111 = addVectors(origin, va, vb, vc);

      const edges = [
        [p000, p100], [p000, p010], [p000, p001],
        [p100, p110], [p100, p101],
        [p010, p110], [p010, p011],
        [p001, p101], [p001, p011],
        [p110, p111], [p101, p111], [p011, p111],
      ];

      for (const [start, end] of edges) {{
        viewer.addLine({{
          start,
          end,
          color: "#475569",
          linewidth: 2,
        }});
      }}
    }}

    function applyElementStyles() {{
      for (const elem of structure.elements) {{
        const color = vestaColors[elem] ?? "#9ca3af";
        viewer.setStyle({{ elem }}, {{
          sphere: {{
            scale: 0.24,
            color,
          }},
          stick: {{
            radius: 0.12,
            color,
          }},
        }});
      }}
    }}

    function positionLegend() {{
      const top = Math.round(panelElement.getBoundingClientRect().bottom + 12);
      legendElement.style.top = `${{top}}px`;
    }}

    function syncLegendToggle() {{
      const collapsed = legendElement.classList.contains("collapsed");
      legendToggle.textContent = collapsed ? "展开图例" : "收起图例";
      legendToggle.setAttribute("aria-expanded", String(!collapsed));
      positionLegend();
    }}

    legendToggle.addEventListener("click", () => {{
      legendElement.classList.toggle("collapsed");
      syncLegendToggle();
    }});

    function init() {{
      viewer.addModel(xyzData, "xyz");
      applyElementStyles();
      if (structure.showUnitCell) {{
        drawUnitCell();
      }}
      viewer.zoomTo();
      viewer.render();
      syncLegendToggle();
    }}

    window.addEventListener("resize", () => {{
      viewer.resize();
      viewer.render();
      positionLegend();
    }});

    init();
  </script>
</body>
</html>
"""


def render_structure_html(structure: dict, viewer_js: str, default_fps: float) -> tuple[str, str]:
    if len(structure["frames"]) > 1:
        return build_html(structure, viewer_js, default_fps), "animated"
    return build_static_html(structure, viewer_js), "static"


def main() -> None:
    args = parse_args()
    if args.stride < 1:
        raise ValueError("Stride must be a positive integer")
    if args.fps <= 0:
        raise ValueError("FPS must be positive")

    script_dir = Path(__file__).resolve().parent
    viewer_js = load_viewer_library()

    if args.input_file is not None:
        input_path = args.input_file.resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input structure file not found: {input_path}")

        output_path = (args.output or make_default_output_path(input_path)).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        structure = parse_structure_by_content(input_path, args.stride)
        html_text, mode = render_structure_html(structure, viewer_js, args.fps)
        output_path.write_text(html_text, encoding="utf-8")

        print(f"{input_path.name} -> {output_path} ({mode}, {len(structure['frames'])} frame(s))")
        print("HTML is self-contained and does not require a separate 3Dmol-min.js file.")
        return

    if args.output is not None:
        print("Batch mode ignores --output and writes one HTML next to each recognized structure file.")

    search_dirs = [Path.cwd(), script_dir]
    discovered = discover_parseable_structures(search_dirs, args.stride)
    if not discovered:
        searched = ", ".join(str(directory) for directory in search_dirs)
        raise FileNotFoundError(f"No supported structure files were recognized in: {searched}")

    for input_path, structure in discovered:
        output_path = make_default_output_path(input_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        html_text, mode = render_structure_html(structure, viewer_js, args.fps)
        output_path.write_text(html_text, encoding="utf-8")
        print(f"{input_path.name} -> {output_path} ({mode}, {len(structure['frames'])} frame(s))")

    print("HTML is self-contained and does not require a separate 3Dmol-min.js file.")


if __name__ == "__main__":
    main()
