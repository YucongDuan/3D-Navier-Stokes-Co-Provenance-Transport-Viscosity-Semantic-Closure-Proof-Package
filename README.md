# Yucong Duan: 3D Navier–Stokes Co-Provenance Transport–Viscosity Semantic Closure Proof Package

Created by Yucong Duan (段玉聪).

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


<!-- DIKWP-SOURCE-VISIBILITY-START -->
## Browse source / 浏览源码

[Source index / 源码入口](SOURCE_INDEX.md) expands the retained archive distribution into browsable files, with archive hashes and per-project provenance. Runtime tests: NOT_RUN.

原始压缩包 保留；新增可浏览源码、哈希与来源记录。运行与测试尚未执行，详情见源码入口。
<!-- DIKWP-SOURCE-VISIBILITY-END -->


## Related research navigation / 相关研究导航

Research navigation, not verified software dependencies. / 研究导航，不代表已验证的软件依赖关系。

- [Gauge-Orbit-Closed-Excitation-Quantum-Semantic-Closure-System](https://github.com/YucongDuan/Gauge-Orbit-Closed-Excitation-Quantum-Semantic-Closure-System)
- [Navier-Stokes-BCSTC](https://github.com/YucongDuan/Navier-Stokes-BCSTC)
- [Schanuel-s-Conjecture-Mesh8.0-Semantic-Closure-Package](https://github.com/YucongDuan/Schanuel-s-Conjecture-Mesh8.0-Semantic-Closure-Package)
- [Twin-Prime-Semantic-Closure-Package](https://github.com/YucongDuan/Twin-Prime-Semantic-Closure-Package)
- [DIKWP-COVARIA-OS](https://github.com/YucongDuan/DIKWP-COVARIA-OS)

## Current interface presentation

[Open the interface source](source-distribution/Duan_3D_Navier_Stokes_MESH80_Bilingual_Proof_Package-4b3b3eab11/source/dashboards/navier_stokes_mesh80_dashboard_en.html) from the current repository download. See [interface and authorship notes](INTERFACE_NOTES.md) for English coverage, report generation and validation scope.
