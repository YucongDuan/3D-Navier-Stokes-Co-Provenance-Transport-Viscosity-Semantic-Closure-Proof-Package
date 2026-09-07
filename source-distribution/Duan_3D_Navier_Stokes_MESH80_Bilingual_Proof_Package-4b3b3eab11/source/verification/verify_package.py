#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'verification'/'SHA256SUMS.txt'
RUNTIME=ROOT/'runtime'/'DIKWP_MESH80_CORE.pyz'
RUNS=[ROOT/'certificates'/'navier_stokes_mesh80_run_output_cn.json',ROOT/'certificates'/'navier_stokes_mesh80_run_output_en.json']

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def verify_manifest()->bool:
    ok=True
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        digest,rel=line.split('  ',1)
        p=ROOT/rel
        actual=sha256(p) if p.exists() else 'MISSING'
        good=(actual==digest)
        print(f"[{'PASS' if good else 'FAIL'}] SHA256 {rel}")
        ok &= good
    return ok

def verify_replay()->bool:
    ok=True
    for run in RUNS:
        proc=subprocess.run([sys.executable,str(RUNTIME),'replay',str(run)],cwd=ROOT,text=True,capture_output=True)
        good=proc.returncode==0
        print(f"[{'PASS' if good else 'FAIL'}] replay {run.name}")
        if proc.stdout.strip(): print(proc.stdout.strip())
        if not good and proc.stderr.strip(): print(proc.stderr.strip())
        ok &= good
    return ok

def main()->int:
    if not MANIFEST.exists():
        print('[FAIL] manifest missing')
        return 2
    ok=verify_manifest() and verify_replay()
    print('PACKAGE_VERIFICATION_PASS' if ok else 'PACKAGE_VERIFICATION_FAIL')
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
