#!/usr/bin/env python3
"""Render the saved visible QGIS canvas to a PNG for visual verification."""

from __future__ import annotations

import argparse
import gc
import os
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsApplication,
    QgsCoordinateTransform,
    QgsMapRendererParallelJob,
    QgsMapSettings,
    QgsProject,
    QgsRectangle,
)


def project_xml(path: Path):
    if path.suffix.casefold() == ".qgz":
        with ZipFile(path) as archive:
            qgs_name = next(name for name in archive.namelist() if name.endswith(".qgs"))
            return ElementTree.fromstring(archive.read(qgs_name))
    return ElementTree.parse(path).getroot()


def saved_extent(path: Path):
    root = project_xml(path)
    extent = root.find("./mapcanvas/extent")
    if extent is None:
        return None
    values = [extent.findtext(name) for name in ("xmin", "ymin", "xmax", "ymax")]
    if any(value is None for value in values):
        return None
    return QgsRectangle(*(float(value) for value in values))


def combined_extent(project: QgsProject, layers):
    result = QgsRectangle()
    for layer in layers:
        extent = QgsRectangle(layer.extent())
        if layer.crs() != project.crs():
            transform = QgsCoordinateTransform(
                layer.crs(), project.crs(), project.transformContext()
            )
            extent = transform.transformBoundingBox(extent)
        result.combineExtentWith(extent)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=1800)
    parser.add_argument("--height", type=int, default=1200)
    parser.add_argument("--dpi", type=float, default=144)
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0 or args.dpi <= 0:
        raise ValueError("Width, height, and DPI must be positive.")

    project_path = args.project.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    project = None
    qgis = QgsApplication([], False)
    qgis.initQgis()
    try:
        project = QgsProject()
        if not project.read(str(project_path)):
            raise RuntimeError(f"QGIS could not read {project_path}")
        root = project.layerTreeRoot()
        layers = [
            layer
            for layer in root.layerOrder()
            if layer.isValid()
            and root.findLayer(layer.id()) is not None
            and root.findLayer(layer.id()).isVisible()
        ]
        if not layers:
            raise RuntimeError("The project has no visible valid layers.")

        extent = saved_extent(project_path) or combined_extent(project, layers)
        settings = QgsMapSettings()
        settings.setLayers(layers)
        settings.setDestinationCrs(project.crs())
        settings.setTransformContext(project.transformContext())
        settings.setExtent(extent)
        settings.setOutputSize(QSize(args.width, args.height))
        settings.setOutputDpi(args.dpi)
        settings.setBackgroundColor(QColor("#f7f6f2"))

        job = QgsMapRendererParallelJob(settings)
        job.start()
        job.waitForFinished()
        image = job.renderedImage()
        if image.isNull() or not image.save(str(output_path)):
            raise RuntimeError(f"Could not write {output_path}")
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
