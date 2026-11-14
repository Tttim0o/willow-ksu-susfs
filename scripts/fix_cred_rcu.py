#!/usr/bin/env python3
# FloppyKernel (willow/ginkgo, 4.14) ma struct cred.usage ako atomic_long_t, nie atomic_t.
# KernelSU v0.9.5 ale do include/linux/cred.h injektuje get_cred_rcu() cez atomic_inc_not_zero,
# co je pre atomic_t -> type error. Opravime sablonu v KSU Makefile aj uz injektovanu funkciu,
# aby pouzivali atomic_long_inc_not_zero. Idempotentne.
import re, sys, pathlib

targets = [
    "drivers/kernelsu/kernel/Makefile",   # sablona, z ktorej sa injektuje
    "include/linux/cred.h",               # uz injektovana funkcia (ak build uz prebehol)
]
old = "atomic_inc_not_zero(&nonconst_cred->usage)"
new = "atomic_long_inc_not_zero(&nonconst_cred->usage)"

changed = False
for rel in targets:
    p = pathlib.Path(rel)
    if not p.exists():
        continue
    txt = p.read_text()
    if old in txt:
        p.write_text(txt.replace(old, new))
        print(f"fix_cred_rcu: opravene {rel}")
        changed = True
    elif new in txt:
        print(f"fix_cred_rcu: {rel} uz opravene")

if not changed:
    print("fix_cred_rcu: nic na opravu (mozno iny strom)")
