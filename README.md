# Yucong Duan: 3D Navier–Stokes Co-Provenance Transport–Viscosity Semantic Closure Proof Package

Version: MESH8.0 / `MESH80_DIKWP_CORE_ONLY`

## Contents

- `reports/`: complete Chinese and English Word reports.
- `certificates/`: bilingual run specifications, run artifacts, and bidirectional replay results.
- `dashboards/`: offline Chinese and English proof dashboards.
- `runtime/`: DIKWP-MESH 8.0 core bidirectional semantic-generation runtime.
- `figures/`: original bilingual proof diagrams.
- `source/`: figure and report generation scripts.
- `verification/`: proof claims, release metadata, and local integrity checks.

## Core claim

Inside the N1–N8 provenance-complete semantic system, the package proves that a zero-force, positive-viscosity, three-dimensional incompressible flow has a unique smooth continuable normal form at every finite time. The proof is organized by one momentum provenance, co-provenance transport, endogenous viscous elimination of registered differences, pressure completeness closure, and non-generation of a finite-time singular packet.

Final recognition as a solution of the classical Navier–Stokes Millennium Problem is recorded separately through the C1–C8 bidirectional fidelity interfaces and independent external certification. A successful runtime replay is not represented as certification by the classical PDE community.

## Quick verification

Run from this directory:

```bash
python verification/verify_package.py
```

Or replay the bilingual artifacts directly:

```bash
python runtime/DIKWP_MESH80_CORE.pyz replay certificates/navier_stokes_mesh80_run_output_cn.json
python runtime/DIKWP_MESH80_CORE.pyz replay certificates/navier_stokes_mesh80_run_output_en.json
```
