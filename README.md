# Redmi Note 8T (willow) — KernelSU-Next + SUSFS kernel for PixelOS 17 (Android 17)

Experimentálny kernel pre **Xiaomi Redmi Note 8T** (codename **willow**, SoC SM6125 / Snapdragon 665)
na **PixelOS 17.0 (Android 17)**, s **KernelSU** a **SUSFS**. Bez NetHunter.

Stock kernel tohto buildu je `4.14.357-openela-perf` (non-GKI). Tento repozitár stavia na
rovnakej verzii (4.14.357), aby **vermagic modulov sedel so stockom** a vendor `.ko` moduly
(wlan, atď.) sa načítali.

## Stav

- **NETESTOVANÝ, EXPERIMENTÁLNY.** Build je pripravený AI (Claude) a nebol overený na zariadení.
- **NEFLASHUJ naslepo.** Najprv `fastboot boot` (dočasne), až po overení `fastboot flash boot`.
- Vždy si zálohuj stock `boot.img`.
- Predchádzajúci pokus (FloppyKernel KSU-Next+SUSFS) sa na Androide 17 bootloopoval. Tento build
  preto **vypína SUSFS funkcie, ktoré na non-GKI spôsobujú bootloop** (hlavne `mnt_id_reorder`)
  a robí minimálnu, čistú integráciu namiesto plne upraveného custom kernelu.

## Čo je kde

- `.github/workflows/build.yml` — CI build (klonuje kernel zdroj, KSU-Next, SUSFS, zbuildí, zbalí AnyKernel3).
- `scripts/` — idempotentné Python fixy na patch hunky, ktoré na tomto strome nesadnú čisto
  (rovnaký prístup ako pri Nothing Spacewar kerneli).

## Non-GKI / 4.14 poznámky

- KernelSU **1.0+ zrušil podporu non-GKI**, preto sa používa **tiann/KernelSU `v0.9.5`** (posledná
  verzia s non-GKI podporou). SUSFS `kernel-4.14` patch je písaný presne na túto verziu a sadne na
  **0 rejectov**. (KernelSU-Next sa sem nehodí: jeho `next` vetva vyžaduje `CONFIG_KPROBES`, a
  pridaním kprobes k manuálnym hookom FloppyKernelu vzniká dvojité hookovanie — pravdepodobná
  príčina bootloopu pôvodného FloppyKernel KSU buildu na A17.)
- **Kprobe hooky sú vypnuté** (`#ifdef CONFIG_KPROBES` → `#if defined(CONFIG_KPROBES) && 0`). KSU
  ide cez **manuálne `ksu_handle_*` hooky**, ktoré FloppyKernel už má v `fs/*.c`. Runtime log hláška
  „KPROBES is disabled, KernelSU may not work" je preto **očakávaná**, nie chyba.
- SUSFS na non-GKI nemá `SUS_SU`; `mnt_id_reorder` tu bootloopuje, preto sú vypnuté.
- `scripts/fix_cred_rcu.py`: FloppyKernel má `struct cred.usage` ako `atomic_long_t`, takže
  injektovaný `get_cred_rcu()` musí použiť `atomic_long_inc_not_zero`.

## Odkazy

- Kernel base: FloppyKernel (`FlopKernel-Series/flop_trinket-mi_kernel`, SM6125/trinket)
- KernelSU: `tiann/KernelSU` tag `v0.9.5`
- SUSFS: `gitlab.com/simonpunk/susfs4ksu` (branch `kernel-4.14`)
- AnyKernel3: `osm0sis/AnyKernel3`
