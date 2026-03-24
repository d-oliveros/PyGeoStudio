# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyGeoStudio is a Python library for programmatically reading, modifying, and writing GeoStudio `.gsz` files (geotechnical simulation software). It enables automation of numerical model processing, parametric studies, calibration, and result extraction without the GeoStudio GUI.

## Build & Development Commands

```bash
# Install for development
pip install -e .

# Install normally
pip install .

# Build documentation
cd docs && make html      # Linux/Mac
cd docs && make.bat html  # Windows

# Run example scripts (serves as integration tests)
bash examples/run_examples.sh
```

There is no formal test suite. The `examples/` directory contains integration-style example scripts organized by category (basics, calibrations, datasets, geometry, parametric, results).

## Architecture

### File Format

GeoStudio `.gsz` files are **ZIP archives** containing:
- XML metadata describing analyses, materials, geometry, boundary conditions
- PLY mesh files for each meshed geometry

### Class Hierarchy

All property containers inherit from `BasePropertiesClass`, which provides dictionary-style access (`obj["Property"]`) via `__getitem__`/`__setitem__`.

**`GeoStudioFile`** (`PyGeoStudio.py`) is the main entry point. It parses the `.gsz` ZIP, builds the XML tree, and owns collections of:
- `Analysis` — simulation configuration + `TimeIncrements` + associated `Results`
- `Geometry` — points, lines, regions
- `Mesh` — PLY-format mesh data
- `Material` — stress-strain and hydraulic properties, references `Function` objects
- `Context` — links materials to geometry regions and applies boundary conditions
- `Function` — XY data curves used for material/boundary properties
- `Dataset` — tabular input data
- `Reinforcement` — anchors, piles, geosynthetics

### Key Relationships

- Each `Analysis` references a `Geometry`, `Mesh`, and `Context` by ID
- `Context` maps region IDs → material IDs and boundary IDs → BC IDs
- `Material` hydraulic properties reference `Function` objects by ID (e.g., `KFn`, `VolWCFn`)
- `Results` are extracted from the ZIP archive and provide snapshots by variable name and time step

### Simulation Execution

`utils.py` provides `run()` which invokes `GeoCmd.exe` (Windows CLI for GeoStudio) as a subprocess. The executable path is resolved from the system PATH.

## Dependencies

Core: `numpy`, `matplotlib`, `plyfile`, `bs4` (BeautifulSoup), `lxml`, `prettytable`

## Conventions

- Property access is dictionary-style: `material["Hydraulic"]["KSat"] = 1e-6`
- Lookup methods follow `getXByName()` / `getXByID()` pattern
- `show*()` methods print summary tables using `prettytable`
- XML manipulation uses `lxml.etree` throughout
- Version: 0.4.4, License: GPLv3, Python: >=3.6
