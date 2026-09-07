# 段玉聪：三维 Navier–Stokes 同源输运—黏性消解语义闭环证明包

版本：MESH8.0 / `MESH80_DIKWP_CORE_ONLY`

## 交付内容

- `reports/`：中英文完整 Word 报告。
- `certificates/`：中英文运行规范、运行产物与双向回放结果。
- `dashboards/`：可离线打开的中英文证明仪表板。
- `runtime/`：DIKWP-MESH 8.0 核心双向语义生成运行时。
- `figures/`：报告使用的原创中英文结构图。
- `source/`：图形与报告生成脚本。
- `verification/`：证明声明、发布信息及本地完整性验证工具。

## 核心证明声明

本包在 N1—N8 来源完备语义系统内完成如下内部定理：无外力、正黏性的三维不可压缩流，在任意有限时刻均形成唯一、可继续的光滑正常形。证明以单一动量来源、同源输运、正黏性内生差异消解、压力完整性约束以及有限时间奇性非生成为核心。

经典三维 Navier–Stokes 千禧年问题的最终认定，仍与 C1—C8 的双向保真编译及外部独立认证分层记录。本包不把运行哈希或机器回放本身表述为经典 PDE 共同体认证。

## 快速验证

在本目录运行：

```bash
python verification/verify_package.py
```

也可分别回放中英文运行产物：

```bash
python runtime/DIKWP_MESH80_CORE.pyz replay certificates/navier_stokes_mesh80_run_output_cn.json
python runtime/DIKWP_MESH80_CORE.pyz replay certificates/navier_stokes_mesh80_run_output_en.json
```
