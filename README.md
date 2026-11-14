# Redmi Note 8T (willow) — KernelSU-Next + SUSFS kernel for PixelOS 17 (Android 17)

Experimentálny kernel pre **Xiaomi Redmi Note 8T** (codename **willow**, SoC SM6125 / Snapdragon 665)
na **PixelOS 17.0 (Android 17)**, s **KernelSU-Next** a **SUSFS**. Bez NetHunter.

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

- KernelSU **1.0+ zrušil podporu non-GKI**. Používa sa **KernelSU-Next legacy** vetva s manuálnymi
  hookmi v kerneli.
- SUSFS na non-GKI nemá `SUS_SU`; `mnt_id_reorder` tu bootloopuje, preto je vypnutý.

## Odkazy

- Kernel base: FloppyKernel (`FlopKernel-Series/flop_trinket-mi_kernel`, SM6125/trinket)
- KernelSU-Next: `KernelSU-Next/KernelSU-Next` (legacy)
- SUSFS: `gitlab.com/simonpunk/susfs4ksu` (branch `kernel-4.14`)
- AnyKernel3: `osm0sis/AnyKernel3`
