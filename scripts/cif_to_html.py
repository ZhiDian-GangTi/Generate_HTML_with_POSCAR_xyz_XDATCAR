#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import shlex
from pathlib import Path


CELL_TAGS = {
    "_cell_length_a": "a",
    "_cell_length_b": "b",
    "_cell_length_c": "c",
    "_cell_angle_alpha": "alpha",
    "_cell_angle_beta": "beta",
    "_cell_angle_gamma": "gamma",
}

ATOM_LOOP_REQUIRED = {
    "_atom_site_label",
    "_atom_site_fract_x",
    "_atom_site_fract_y",
    "_atom_site_fract_z",
}

NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
ELEMENT_RE = re.compile(r"[A-Za-z]{1,2}")
INT_RE = re.compile(r"^[+-]?\d+$")

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
        description="Convert a CIF, POSCAR/CONTCAR, or XYZ file into a local interactive HTML crystal viewer."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="Path to the input structure file. If omitted, the script uses the only supported structure file in the current working directory.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML path. Defaults to <input>.html",
    )
    parser.add_argument(
        "--supercell",
        nargs=3,
        metavar=("A", "B", "C"),
        type=int,
        default=(1, 1, 1),
        help="Default supercell shown when the HTML opens",
    )
    return parser.parse_args()


def parse_cif_number(value: str) -> float:
    value = value.strip()
    match = NUMBER_RE.match(value)
    if not match:
        raise ValueError(f"Cannot parse CIF number from {value!r}")
    return float(match.group(0))


def normalize_element(raw_symbol: str | None, label: str) -> str:
    for candidate in (raw_symbol, label):
        if not candidate or candidate in {"?", "."}:
            continue
        match = ELEMENT_RE.search(candidate)
        if match:
            symbol = match.group(0)
            return symbol[0].upper() + symbol[1:].lower()
    raise ValueError(f"Cannot determine element symbol for atom label {label!r}")


def is_int_token(token: str) -> bool:
    return bool(INT_RE.fullmatch(token.strip()))


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


def invert_lattice_vectors(a_vec: list[float], b_vec: list[float], c_vec: list[float]) -> list[list[float]]:
    matrix = [
        [a_vec[0], b_vec[0], c_vec[0]],
        [a_vec[1], b_vec[1], c_vec[1]],
        [a_vec[2], b_vec[2], c_vec[2]],
    ]

    det = (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )
    if abs(det) < 1e-12:
        raise ValueError("Lattice vectors are singular and cannot be inverted")

    inv_det = 1.0 / det
    return [
        [
            (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) * inv_det,
            (matrix[0][2] * matrix[2][1] - matrix[0][1] * matrix[2][2]) * inv_det,
            (matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1]) * inv_det,
        ],
        [
            (matrix[1][2] * matrix[2][0] - matrix[1][0] * matrix[2][2]) * inv_det,
            (matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]) * inv_det,
            (matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2]) * inv_det,
        ],
        [
            (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]) * inv_det,
            (matrix[0][1] * matrix[2][0] - matrix[0][0] * matrix[2][1]) * inv_det,
            (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) * inv_det,
        ],
    ]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    ]


def build_labels(elements: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    labels: list[str] = []
    for elem in elements:
        counts[elem] = counts.get(elem, 0) + 1
        labels.append(f"{elem}{counts[elem]}")
    return labels


def cell_from_vectors(a_vec: list[float], b_vec: list[float], c_vec: list[float]) -> dict[str, float]:
    a = vector_length(a_vec)
    b = vector_length(b_vec)
    c = vector_length(c_vec)

    def safe_angle(v1: list[float], v2: list[float]) -> float:
        cosine = dot(v1, v2) / (vector_length(v1) * vector_length(v2))
        cosine = max(-1.0, min(1.0, cosine))
        return math.degrees(math.acos(cosine))

    return {
        "a": a,
        "b": b,
        "c": c,
        "alpha": safe_angle(b_vec, c_vec),
        "beta": safe_angle(a_vec, c_vec),
        "gamma": safe_angle(a_vec, b_vec),
    }


def tokenize_line(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return []
    return shlex.split(stripped, posix=True)


def parse_cif(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    scalar_values: dict[str, str] = {}
    atom_rows: list[dict[str, object]] | None = None

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if stripped.lower() == "loop_":
            i += 1
            columns: list[str] = []

            while i < len(lines):
                tokens = tokenize_line(lines[i])
                if not tokens:
                    i += 1
                    continue
                if tokens[0].startswith("_"):
                    columns.append(tokens[0])
                    i += 1
                    continue
                break

            data_tokens: list[str] = []
            while i < len(lines):
                next_stripped = lines[i].strip()
                if not next_stripped or next_stripped.startswith("#"):
                    i += 1
                    continue
                lowered = next_stripped.lower()
                if (
                    next_stripped.startswith("_")
                    or lowered == "loop_"
                    or lowered.startswith("data_")
                    or lowered.startswith("save_")
                ):
                    break
                data_tokens.extend(tokenize_line(lines[i]))
                i += 1

            if columns and ATOM_LOOP_REQUIRED.issubset(columns):
                if len(data_tokens) % len(columns) != 0:
                    raise ValueError("CIF atom loop token count does not match column count")

                index = {column: idx for idx, column in enumerate(columns)}
                atom_rows = []
                for row_start in range(0, len(data_tokens), len(columns)):
                    row = data_tokens[row_start : row_start + len(columns)]
                    label = row[index["_atom_site_label"]]
                    raw_symbol = row[index["_atom_site_type_symbol"]] if "_atom_site_type_symbol" in index else None
                    atom_rows.append(
                        {
                            "label": label,
                            "elem": normalize_element(raw_symbol, label),
                            "frac": [
                                parse_cif_number(row[index["_atom_site_fract_x"]]),
                                parse_cif_number(row[index["_atom_site_fract_y"]]),
                                parse_cif_number(row[index["_atom_site_fract_z"]]),
                            ],
                        }
                    )
            continue

        tokens = tokenize_line(lines[i])
        if tokens and tokens[0].startswith("_") and len(tokens) >= 2:
            scalar_values[tokens[0]] = tokens[1]
        i += 1

    if atom_rows is None:
        raise ValueError("Could not find an atom loop with fractional coordinates in the CIF file")

    cell = {}
    for cif_tag, short_name in CELL_TAGS.items():
        if cif_tag not in scalar_values:
            raise ValueError(f"Missing required CIF cell tag: {cif_tag}")
        cell[short_name] = parse_cif_number(scalar_values[cif_tag])

    return {
        "title": path.stem,
        "cell": cell,
        "atoms": atom_rows,
    }


def parse_poscar(path: Path) -> dict:
    lines = [line.rstrip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    lines = [line for line in lines if line.strip()]
    if len(lines) < 8:
        raise ValueError("POSCAR/CONTCAR file is too short")

    title = lines[0].strip() or path.stem
    scale_tokens = lines[1].split()
    raw_vectors = [parse_float_triplet(lines[2]), parse_float_triplet(lines[3]), parse_float_triplet(lines[4])]

    if len(scale_tokens) == 1:
        scale_value = float(scale_tokens[0])
        if scale_value < 0:
            raw_volume = abs(determinant_from_vectors(*raw_vectors))
            if raw_volume <= 0:
                raise ValueError("POSCAR lattice volume must be positive")
            scale_factor = (abs(scale_value) / raw_volume) ** (1.0 / 3.0)
        else:
            scale_factor = scale_value
        vectors = [[component * scale_factor for component in vector] for vector in raw_vectors]
    elif len(scale_tokens) == 3:
        scale_factors = [float(token) for token in scale_tokens]
        vectors = [
            [raw_vectors[row][col] * scale_factors[col] for col in range(3)]
            for row in range(3)
        ]
    else:
        raise ValueError("POSCAR scale line must contain one or three numbers")

    line_index = 5
    symbol_tokens = lines[line_index].split()
    if symbol_tokens and all(is_int_token(token) for token in symbol_tokens):
        species = []
        counts = [int(token) for token in symbol_tokens]
        line_index += 1
    else:
        species = [normalize_element(token, token) for token in symbol_tokens]
        line_index += 1
        counts_tokens = lines[line_index].split()
        if not counts_tokens or not all(is_int_token(token) for token in counts_tokens):
            raise ValueError("Could not parse POSCAR atom counts line")
        counts = [int(token) for token in counts_tokens]
        line_index += 1
        if len(species) != len(counts):
            raise ValueError("POSCAR species line and counts line have different lengths")

    if line_index >= len(lines):
        raise ValueError("POSCAR is missing coordinate mode line")

    if lines[line_index].strip().lower().startswith("s"):
        line_index += 1
        if line_index >= len(lines):
            raise ValueError("POSCAR is missing coordinate mode line after Selective Dynamics")

    coordinate_mode = lines[line_index].strip().lower()
    if not coordinate_mode:
        raise ValueError("POSCAR coordinate mode line is empty")
    direct_mode = coordinate_mode[0] == "d"
    cartesian_mode = coordinate_mode[0] in {"c", "k"}
    if not direct_mode and not cartesian_mode:
        raise ValueError("POSCAR coordinate mode must be Direct or Cartesian")
    line_index += 1

    atom_count = sum(counts)
    if len(lines) < line_index + atom_count:
        raise ValueError("POSCAR does not contain enough atomic coordinate lines")

    if species:
        elements = [species[idx] for idx, count in enumerate(counts) for _ in range(count)]
    else:
        elements = []

    inverse_vectors = invert_lattice_vectors(*vectors) if cartesian_mode else None
    atoms: list[dict[str, object]] = []
    dynamic_labels: list[str] = []

    for atom_idx in range(atom_count):
        tokens = lines[line_index + atom_idx].split()
        if len(tokens) < 3:
            raise ValueError(f"Invalid POSCAR atom line: {lines[line_index + atom_idx]!r}")

        coords = [float(tokens[0]), float(tokens[1]), float(tokens[2])]
        if direct_mode:
            frac = coords
        else:
            frac = matvec(inverse_vectors, coords)

        if elements:
            elem = elements[atom_idx]
        else:
            raw_symbol = next(
                (
                    token
                    for token in tokens[3:]
                    if token and token[0].isalpha() and token[0].upper() not in {"T", "F"}
                ),
                "X",
            )
            elem = normalize_element(raw_symbol, raw_symbol) if raw_symbol != "X" else "X"
            dynamic_labels.append(elem)

        atoms.append(
            {
                "label": "",
                "elem": elem,
                "frac": frac,
            }
        )

    labels = build_labels([atom["elem"] for atom in atoms])
    for atom, label in zip(atoms, labels, strict=True):
        atom["label"] = label

    return {
        "title": title,
        "cell": cell_from_vectors(*vectors),
        "vectors": vectors,
        "atoms": atoms,
    }


def parse_xyz(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) < 2:
        raise ValueError("XYZ file is too short")

    header_tokens = lines[0].split()
    if not header_tokens or not is_int_token(header_tokens[0]):
        raise ValueError("XYZ first line must start with the atom count")

    atom_count = int(header_tokens[0])
    if atom_count <= 0:
        raise ValueError("XYZ atom count must be positive")
    if len(lines) < atom_count + 2:
        raise ValueError("XYZ file does not contain enough atom lines")

    title = lines[1].strip() or path.stem
    elements: list[str] = []
    positions: list[list[float]] = []
    for line in lines[2 : 2 + atom_count]:
        tokens = line.split()
        if len(tokens) < 4:
            raise ValueError(f"Invalid XYZ atom line: {line!r}")
        elem = normalize_element(tokens[0], tokens[0])
        pos = [float(tokens[1]), float(tokens[2]), float(tokens[3])]
        elements.append(elem)
        positions.append(pos)

    minima = [min(position[idx] for position in positions) for idx in range(3)]
    maxima = [max(position[idx] for position in positions) for idx in range(3)]
    padding = 2.0
    lengths = [max(maxima[idx] - minima[idx] + 2 * padding, 5.0) for idx in range(3)]
    origin = [minima[idx] - padding for idx in range(3)]
    vectors = [
        [lengths[0], 0.0, 0.0],
        [0.0, lengths[1], 0.0],
        [0.0, 0.0, lengths[2]],
    ]

    labels = build_labels(elements)
    atoms = []
    for elem, label, pos in zip(elements, labels, positions, strict=True):
        frac = [(pos[idx] - origin[idx]) / lengths[idx] for idx in range(3)]
        atoms.append(
            {
                "label": label,
                "elem": elem,
                "frac": frac,
            }
        )

    return {
        "title": title,
        "cell": cell_from_vectors(*vectors),
        "vectors": vectors,
        "atoms": atoms,
    }


def parse_structure_file(path: Path) -> dict:
    suffix = path.suffix.lower()
    name = path.name.lower()

    if suffix == ".cif":
        return parse_cif(path)
    if suffix == ".xyz":
        return parse_xyz(path)
    if suffix in {".vasp", ".poscar", ".contcar"} or name in {"poscar", "contcar"}:
        return parse_poscar(path)

    raise ValueError(
        "Unsupported input format. Supported inputs are .cif, .xyz, POSCAR, CONTCAR, and .vasp files."
    )


def is_supported_structure_path(path: Path) -> bool:
    suffix = path.suffix.lower()
    name = path.name.lower()
    return suffix in {".cif", ".xyz", ".vasp", ".poscar", ".contcar"} or name in {"poscar", "contcar"}


def auto_detect_input_file(cwd: Path) -> Path:
    candidates = sorted(
        (
            path
            for path in cwd.iterdir()
            if path.is_file() and is_supported_structure_path(path)
        ),
        key=lambda path: path.name.lower(),
    )

    if not candidates:
        raise FileNotFoundError(
            "No supported structure file was found in the current directory. "
            "Supported inputs are .cif, .xyz, POSCAR, CONTCAR, and .vasp files."
        )

    if len(candidates) > 1:
        joined = ", ".join(path.name for path in candidates)
        raise ValueError(
            "Multiple supported structure files were found in the current directory. "
            f"Please specify one explicitly: {joined}"
        )

    return candidates[0]


def lattice_vectors(cell: dict[str, float]) -> tuple[list[float], list[float], list[float]]:
    alpha = math.radians(cell["alpha"])
    beta = math.radians(cell["beta"])
    gamma = math.radians(cell["gamma"])

    a_vec = [cell["a"], 0.0, 0.0]
    b_vec = [cell["b"] * math.cos(gamma), cell["b"] * math.sin(gamma), 0.0]

    c_x = cell["c"] * math.cos(beta)
    c_y = cell["c"] * (math.cos(alpha) - math.cos(beta) * math.cos(gamma)) / math.sin(gamma)
    c_z_sq = max(cell["c"] ** 2 - c_x ** 2 - c_y ** 2, 0.0)
    c_vec = [c_x, c_y, math.sqrt(c_z_sq)]

    return a_vec, b_vec, c_vec


def build_html(structure: dict, default_supercell: tuple[int, int, int], viewer_js: str) -> str:
    if "vectors" in structure:
        a_vec, b_vec, c_vec = structure["vectors"]
    else:
        a_vec, b_vec, c_vec = lattice_vectors(structure["cell"])
    structure_payload = {
        "title": structure["title"],
        "cell": {
            **structure["cell"],
            "vectors": {
                "a": a_vec,
                "b": b_vec,
                "c": c_vec,
            },
        },
        "atoms": structure["atoms"],
        "defaultSupercell": list(default_supercell),
    }
    payload_json = json.dumps(structure_payload, ensure_ascii=False, indent=2)
    colors_json = json.dumps(VESTA_COLORS, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{structure["title"]}</title>
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

    #controls {{
      position: fixed;
      top: 16px;
      left: 16px;
      right: 16px;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      max-width: 420px;
      background: rgba(255, 255, 255, 0.95);
      border: 1px solid #d1d5db;
      border-radius: 10px;
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
      color: #111827;
      font-size: 13px;
      backdrop-filter: blur(6px);
      touch-action: manipulation;
    }}

    #controls input {{
      width: 56px;
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 13px;
      color: #111827;
      background: #ffffff;
    }}

    #controls button {{
      padding: 6px 12px;
      border: 1px solid #0f172a;
      border-radius: 8px;
      background: #0f172a;
      color: #ffffff;
      font-size: 13px;
      cursor: pointer;
    }}

    #controls button:hover {{
      background: #1e293b;
    }}

    @media (max-width: 640px) {{
      #controls {{
        top: 12px;
        left: 12px;
        right: 12px;
        max-width: none;
        padding: 10px;
      }}

      #controls input {{
        width: 48px;
      }}
    }}
  </style>
</head>
<body>
  <div id="viewer"></div>

  <form id="controls">
    <span>Supercell</span>
    <input id="supercell-a" type="number" min="1" step="1" value="{default_supercell[0]}" aria-label="supercell a">
    <input id="supercell-b" type="number" min="1" step="1" value="{default_supercell[1]}" aria-label="supercell b">
    <input id="supercell-c" type="number" min="1" step="1" value="{default_supercell[2]}" aria-label="supercell c">
    <button type="submit">Apply</button>
  </form>

  <script>
{viewer_js}
  </script>
  <script>
    const structure = {payload_json};
    const vestaColors = {colors_json};
    const viewerElement = document.getElementById("viewer");
    const viewer = $3Dmol.createViewer("viewer", {{ backgroundColor: "white" }});
    const inputs = {{
      a: document.getElementById("supercell-a"),
      b: document.getElementById("supercell-b"),
      c: document.getElementById("supercell-c"),
    }};
    const cellVectors = structure.cell.vectors;
    const state = {{
      expandedAtoms: [],
      labelAtoms: [],
      labelsVisible: false,
      restoreTimer: null,
    }};

    function parsePositiveInt(value, fallback) {{
      const parsed = Number.parseInt(value, 10);
      return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
    }}

    function scaleVector(vector, factor) {{
      return {{
        x: vector[0] * factor,
        y: vector[1] * factor,
        z: vector[2] * factor,
      }};
    }}

    function offsetPosition(position, amount) {{
      return {{
        x: position.x + amount,
        y: position.y + amount,
        z: position.z + amount,
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

    function fractionalToCartesian(frac, shift) {{
      return addVectors(
        scaleVector(cellVectors.a, frac[0] + shift[0]),
        scaleVector(cellVectors.b, frac[1] + shift[1]),
        scaleVector(cellVectors.c, frac[2] + shift[2])
      );
    }}

    function buildSupercellAtoms(supercell) {{
      const expanded = [];
      for (let i = 0; i < supercell[0]; i += 1) {{
        for (let j = 0; j < supercell[1]; j += 1) {{
          for (let k = 0; k < supercell[2]; k += 1) {{
            for (const atom of structure.atoms) {{
              expanded.push({{
                label: atom.label,
                elem: atom.elem,
                replica: [i, j, k],
                position: fractionalToCartesian(atom.frac, [i, j, k]),
              }});
            }}
          }}
        }}
      }}
      return expanded;
    }}

    function drawSupercellBox(supercell) {{
      const origin = {{ x: 0, y: 0, z: 0 }};
      const va = scaleVector(cellVectors.a, supercell[0]);
      const vb = scaleVector(cellVectors.b, supercell[1]);
      const vc = scaleVector(cellVectors.c, supercell[2]);

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

    function applyElementStyles(expandedAtoms) {{
      const elements = [...new Set(expandedAtoms.map((atom) => atom.elem))];
      for (const elem of elements) {{
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

    function selectLabelAtoms(expandedAtoms, supercell) {{
      const copies = supercell[0] * supercell[1] * supercell[2];
      const baseCellAtoms = expandedAtoms.filter(
        (atom) => atom.replica[0] === 0 && atom.replica[1] === 0 && atom.replica[2] === 0
      );

      if (copies === 1 && baseCellAtoms.length <= 24) {{
        return baseCellAtoms;
      }}

      const preferredAtoms = baseCellAtoms.filter((atom) => !["O", "H"].includes(atom.elem));
      if (preferredAtoms.length > 0) {{
        return preferredAtoms;
      }}

      return baseCellAtoms;
    }}

    function clearLabelRestoreTimer() {{
      if (state.restoreTimer !== null) {{
        window.clearTimeout(state.restoreTimer);
        state.restoreTimer = null;
      }}
    }}

    function clearLabels(shouldRender = true) {{
      clearLabelRestoreTimer();
      if (!state.labelsVisible) {{
        return;
      }}
      viewer.removeAllLabels();
      state.labelsVisible = false;
      if (shouldRender) {{
        viewer.render();
      }}
    }}

    function addLabels() {{
      if (state.labelsVisible || state.labelAtoms.length === 0) {{
        return;
      }}

      const labelFontSize = state.labelAtoms.length > 18 ? 11 : 14;
      const labelOffset = state.labelAtoms.length > 18 ? 0.12 : 0.16;

      for (const atom of state.labelAtoms) {{
        viewer.addLabel(
          atom.label,
          {{
            position: offsetPosition(atom.position, labelOffset),
            font: "sans-serif",
            fontSize: labelFontSize,
            fontColor: "#0f172a",
            backgroundColor: "#ffffff",
            backgroundOpacity: 0.9,
            borderColor: "#334155",
            borderThickness: 1,
            showBackground: true,
            inFront: true,
          }},
          undefined,
          true
        );
      }}

      state.labelsVisible = true;
      viewer.render();
    }}

    function scheduleLabelRestore(delay = 180) {{
      clearLabelRestoreTimer();
      state.restoreTimer = window.setTimeout(() => {{
        state.restoreTimer = null;
        addLabels();
      }}, delay);
    }}

    function handleInteractionStart() {{
      if (state.labelsVisible) {{
        clearLabels(true);
      }} else {{
        clearLabelRestoreTimer();
      }}
    }}

    function handleInteractionEnd(delay = 180) {{
      scheduleLabelRestore(delay);
    }}

    function renderStructure() {{
      clearLabelRestoreTimer();
      const supercell = [
        parsePositiveInt(inputs.a.value, structure.defaultSupercell[0]),
        parsePositiveInt(inputs.b.value, structure.defaultSupercell[1]),
        parsePositiveInt(inputs.c.value, structure.defaultSupercell[2]),
      ];

      inputs.a.value = supercell[0];
      inputs.b.value = supercell[1];
      inputs.c.value = supercell[2];

      viewer.removeAllModels();
      viewer.removeAllLabels();
      viewer.removeAllShapes();
      state.labelsVisible = false;

      const expandedAtoms = buildSupercellAtoms(supercell);
      state.expandedAtoms = expandedAtoms;
      state.labelAtoms = selectLabelAtoms(expandedAtoms, supercell);
      const xyzLines = [
        String(expandedAtoms.length),
        structure.title,
        ...expandedAtoms.map((atom) =>
          `${{atom.elem}} ${{atom.position.x.toFixed(6)}} ${{atom.position.y.toFixed(6)}} ${{atom.position.z.toFixed(6)}}`
        ),
      ];

      viewer.addModel(xyzLines.join("\\n"), "xyz");
      applyElementStyles(expandedAtoms);

      drawSupercellBox(supercell);
      viewer.zoomTo();
      viewer.render();
      scheduleLabelRestore(60);
    }}

    document.getElementById("controls").addEventListener("submit", (event) => {{
      event.preventDefault();
      renderStructure();
    }});

    viewerElement.addEventListener("pointerdown", () => {{
      handleInteractionStart();
    }}, {{ passive: true }});

    window.addEventListener("pointerup", () => {{
      handleInteractionEnd(180);
    }}, {{ passive: true }});

    viewerElement.addEventListener("wheel", () => {{
      handleInteractionStart();
      handleInteractionEnd(220);
    }}, {{ passive: true }});

    viewerElement.addEventListener("pointercancel", () => {{
      handleInteractionEnd(180);
    }}, {{ passive: true }});

    window.addEventListener("resize", () => {{
      viewer.resize();
      viewer.render();
    }});

    renderStructure();
  </script>
</body>
</html>
"""


def load_viewer_library() -> str:
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "3Dmol-min.js",
        script_dir.parent / "vendor" / "3Dmol-min.js",
    ]
    for source in candidates:
        if source.exists():
            return source.read_text(encoding="utf-8").replace("</script>", "<\\/script>")

    raise FileNotFoundError(
        "3Dmol-min.js was not found. Put it next to cif_to_html.py or in ../vendor/3Dmol-min.js."
    )


def main() -> None:
    args = parse_args()
    if any(value < 1 for value in args.supercell):
        raise ValueError("Supercell dimensions must all be positive integers")

    if args.input_file is None:
        input_path = auto_detect_input_file(Path.cwd()).resolve()
    else:
        input_path = args.input_file.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input structure file not found: {input_path}")

    output_path = (args.output or input_path.with_suffix(".html")).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    structure = parse_structure_file(input_path)
    viewer_js = load_viewer_library()
    html_text = build_html(structure, tuple(args.supercell), viewer_js)
    output_path.write_text(html_text, encoding="utf-8")

    print(f"HTML written to: {output_path}")
    print("HTML is self-contained and does not require a separate 3Dmol-min.js file.")


if __name__ == "__main__":
    main()
