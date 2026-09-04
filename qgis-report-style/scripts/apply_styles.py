#!/usr/bin/env python3
"""Apply captured role-based QML styles to a copy of a QGIS project."""

from __future__ import annotations

import argparse
import gc
import os
import re
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import QgsApplication, QgsProject


STYLE_DIRECTORY = Path(__file__).resolve().parents[1] / "assets" / "styles"
ROLE_ALIASES = {
    "ndvi-continuous": ("ndvi", "ndvi p90", ".ndvi.partial", "ndvi continuous"),
    "surface-height": ("surface height", "surface_height", "dom minus dtm"),
    "wind-power": ("vindkraftverkene", "wind power", "wind farms"),
    "study-boundary": ("study area", "study boundary", "east_of_alta"),
    "habitat-class": ("habitat class", "habitat_class"),
    "ndvi-class": ("ndvi class", "ndvi_class"),
    "height-class": ("height class", "height_class"),
}


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def parse_mapping(value: str) -> tuple[str, str]:
    role, separator, layer_name = value.partition("=")
    if not separator or not role.strip() or not layer_name.strip():
        raise argparse.ArgumentTypeError("Mappings must use ROLE=LAYER_NAME")
    return role.strip(), layer_name.strip()


def inferred_layer(project: QgsProject, role: str):
    aliases = {normalized(alias) for alias in ROLE_ALIASES[role]}
    matches = [
        layer
        for layer in project.mapLayers().values()
        if normalized(layer.name()) in aliases
    ]
    return matches[0] if len(matches) == 1 else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        type=parse_mapping,
        metavar="ROLE=LAYER_NAME",
    )
    args = parser.parse_args()

    project_path = args.project.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if project_path == output_path:
        raise ValueError("Output must not overwrite the input project.")
    if output_path.exists():
        raise FileExistsError(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    explicit = dict(args.map)
    unknown_roles = sorted(set(explicit) - set(ROLE_ALIASES))
    if unknown_roles:
        raise ValueError("Unknown roles: " + ", ".join(unknown_roles))

    project = None
    qgis = QgsApplication([], False)
    qgis.initQgis()
    try:
        project = QgsProject()
        if not project.read(str(project_path)):
            raise RuntimeError(f"QGIS could not read {project_path}")

        applied = []
        skipped = []
        for role in ROLE_ALIASES:
            if role in explicit:
                matches = project.mapLayersByName(explicit[role])
                if len(matches) != 1:
                    raise ValueError(
                        f"Role {role!r} expected one layer named "
                        f"{explicit[role]!r}, found {len(matches)}"
                    )
                layer = matches[0]
            else:
                layer = inferred_layer(project, role)
            if layer is None:
                skipped.append(role)
                continue

            style_path = STYLE_DIRECTORY / f"{role}.qml"
            message, success = layer.loadNamedStyle(str(style_path))
            if not success:
                raise RuntimeError(message or f"Could not load {style_path}")
            layer.triggerRepaint()
            applied.append(f"{role}={layer.name()}")

        if not applied:
            names = ", ".join(sorted(layer.name() for layer in project.mapLayers().values()))
            raise RuntimeError(
                "No layer roles matched. Pass --map ROLE=LAYER_NAME. Layers: " + names
            )
        if not project.write(str(output_path)):
            raise RuntimeError(f"Could not write {output_path}")
        print("Applied: " + ", ".join(applied))
        if skipped:
            print("Unmatched roles: " + ", ".join(skipped))
        print(output_path)
    finally:
        if project is not None:
            project.clear()
            project = None
        gc.collect()
        qgis.exitQgis()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
