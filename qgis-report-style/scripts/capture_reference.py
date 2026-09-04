#!/usr/bin/env python3
"""Capture reusable QML styles and a manifest from the reference project."""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import Qgis, QgsApplication, QgsProject


ROLE_LAYERS = {
    "ndvi-continuous": ".ndvi.partial",
    "surface-height": "surface_height",
    "wind-power": "Vindkraftverkene",
    "study-boundary": "east_of_alta",
    "habitat-class": "habitat_class",
    "ndvi-class": "ndvi_class",
    "height-class": "height_class",
}

LAYOUT_ASSETS = [
    {
        "name": "report-a3-landscape",
        "path": "layouts/report-a3-landscape.qpt",
        "page_size": "A3",
        "orientation": "landscape",
    },
    {
        "name": "report-a4-landscape",
        "path": "layouts/report-a4-landscape.qpt",
        "page_size": "A4",
        "orientation": "landscape",
    },
    {
        "name": "report-a4-portrait-page4",
        "path": "layouts/report-a4-portrait-page4.qpt",
        "page_size": "A4",
        "orientation": "portrait",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()

    project_path = args.project.expanduser().resolve()
    output_directory = args.output_directory.expanduser().resolve()
    styles_directory = output_directory / "styles"
    styles_directory.mkdir(parents=True, exist_ok=True)

    project = None
    qgis = QgsApplication([], False)
    qgis.initQgis()
    try:
        project = QgsProject()
        if not project.read(str(project_path)):
            raise RuntimeError(f"QGIS could not read {project_path}")

        captured = []
        for role, layer_name in ROLE_LAYERS.items():
            matches = project.mapLayersByName(layer_name)
            if len(matches) != 1:
                raise RuntimeError(
                    f"Expected one layer named {layer_name!r}, found {len(matches)}"
                )
            layer = matches[0]
            style_path = styles_directory / f"{role}.qml"
            message, success = layer.saveNamedStyle(str(style_path))
            if not success:
                raise RuntimeError(message or f"Could not save {style_path}")
            node = project.layerTreeRoot().findLayer(layer.id())
            renderer = layer.renderer()
            captured.append(
                {
                    "role": role,
                    "reference_layer": layer_name,
                    "style": str(style_path.relative_to(output_directory)),
                    "provider": layer.providerType(),
                    "visible": bool(node and node.isVisible()),
                    "blend_mode": int(layer.blendMode()),
                    "renderer": renderer.type() if renderer else None,
                }
            )
            print(f"Captured {role}: {style_path}")

        manifest = {
            "version": 1,
            "reference_project": str(project_path),
            "qgis_version": Qgis.QGIS_VERSION,
            "project_crs": project.crs().authid(),
            "layouts": [layout.name() for layout in project.layoutManager().layouts()],
            "layout_assets": LAYOUT_ASSETS,
            "layers": captured,
        }
        (output_directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    finally:
        if project is not None:
            project.clear()
            project = None
        gc.collect()
        qgis.exitQgis()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
