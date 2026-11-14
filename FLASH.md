# FLASH — Redmi Note 8T (willow) KernelSU + SUSFS, PixelOS 17

> **NETESTOVANÝ, EXPERIMENTÁLNY build.** Vždy najprv `fastboot boot`, nikdy nie `flash` naslepo.
> Autor neručí za škody. Flashuješ na vlastné riziko.

---

## 0. Čo potrebuješ

- Odomknutý bootloader (`fastboot oem device-info` → `Device unlocked: true`).
- `adb` + `fastboot` na PC (platform-tools).
- USB kábel, nabitý telefón.
- Flashovateľný zip: **`willow-KSU-SUSFS-20261114.zip`** (poslal som ti ho — AnyKernel3).
- KernelSU manager APK: **tiann/KernelSU `v0.9.5`** (presne táto verzia, nie novšia —
  novší manager nebude vedieť s non-GKI v0.9.5 jadrom komunikovať):
  https://github.com/tiann/KernelSU/releases/tag/v0.9.5 → `KernelSU_v0.9.5_*-release.apk`
- **Záloha stock boot.img** z tvojho PixelOS 17 willow buildu (kritické — pozri krok 1).

---

## 1. Zálohuj stock boot (POVINNÉ)

Z toho istého PixelOS 17 ZIPu, ktorý máš nainštalovaný, vytiahni `boot.img`
(payload_dumper na `payload.bin`), alebo si ho stiahni z recovery. Ulož ako `stock_boot.img`.
Keď niečo zlyhá, vrátiš sa cezeň:

```
fastboot flash boot stock_boot.img
```

---

## 2. Test NAŽIVO bez zápisu (fastboot boot)

AnyKernel zip sa flashuje cez recovery, nie cez `fastboot boot`. Takže najbezpečnejší
test je: nechaj si CI vyrobiť **hotový boot.img** a ten dočasne bootni.

- V CI (GitHub Actions) spusti workflow a do poľa `stock_boot_url` daj priamu URL na svoj
  `stock_boot.img`. Dostaneš `new-boot.img` ako artefakt.
- Potom:

```
adb reboot bootloader
fastboot boot new-boot.img
```

Telefón sa má nabootovať normálne (môže to trvať dlhšie). Ak **bootloopuje**, len odpoj/reštartuj —
na disku sa NIČ nezmenilo, stock kernel je stále na mieste.

Ak nemáš `new-boot.img`, musíš ísť rovno cez recovery (krok 3) — vtedy si NAJPRV sprav Nandroid zálohu v recovery.

---

## 3. Flash cez custom recovery (TWRP/OrangeFox)

Keď `fastboot boot new-boot.img` prešiel a systém beží:

1. `adb reboot recovery` (alebo `fastboot boot twrp.img`).
2. V recovery: **Install** → vyber `willow-KSU-SUSFS-20261114.zip` → swipe.
3. Reboot system.

AnyKernel ti kernel zapíše do `boot` partície (`/dev/block/bootdevice/by-name/boot`, A-only).

---

## 4. Po boote

- Nainštaluj `KernelSU_v0.9.5.apk`, otvor → má ukázať **Working / kernel verzia**.
- V logu uvidíš `KPROBES is disabled, KernelSU may not work` — **toto je OČAKÁVANÉ**,
  KSU ide cez manuálne non-GKI hooky, nie cez kprobes. Ak manager hlási Working, je to OK.
- SUSFS: over cez `susfs` CLI / modul.

---

## 5. Keď to nebootuje / chceš späť stock

```
fastboot flash boot stock_boot.img
```

alebo v recovery obnov Nandroid zálohu.

---

## Presný zdroj / pipeline (čo presne build robí)

Celý build je deterministický a je v tomto repe:

- **CI pipeline:** [`.github/workflows/build.yml`](.github/workflows/build.yml) — presný, overený recept
  (lokálne som ho prešiel, produkuje `Image.gz` + zip). Spúšťa sa cez **Actions → Build willow KSU + SUSFS Kernel → Run workflow**.
- **Vstupy pipeline:**
  - `kernel_ref` (default `a14/flop-general`) — vetva FloppyKernelu (SM6125 base).
  - `stock_boot_url` (nepovinné) — URL na tvoj stock boot.img → výstup `new-boot.img` pre krok 2.

### Presné zdroje a verzie (pinned)

| Komponent | Zdroj | Verzia |
|---|---|---|
| Kernel base | `github.com/FlopKernel-Series/flop_trinket-mi_kernel` | vetva `a14/flop-general` |
| KernelSU | `github.com/tiann/KernelSU` | tag **`v0.9.5`** (posledná non-GKI) |
| SUSFS | `gitlab.com/simonpunk/susfs4ksu` | vetva **`kernel-4.14`** |
| AnyKernel3 | `github.com/osm0sis/AnyKernel3` | master |
| Toolchain | `github.com/kdrag0n/proton-clang` | master (LLVM=1) |
| defconfig | `arch/arm64/configs/vendor/ginkgo-perf_defconfig` | — |

### Čo pipeline spraví (poradie krokov v build.yml)

1. Klon FloppyKernel (`kernel_ref`).
2. Proton clang.
3. SUSFS do stromu: `cp fs/* include/linux/*`, aplikuj `50_add_susfs_in_kernel-4.14.patch`;
   reject fixy [`scripts/fix_mount_h.py`](scripts/fix_mount_h.py), [`scripts/fix_task_mmu.py`](scripts/fix_task_mmu.py) (gated — bežia len ak treba).
4. KernelSU v0.9.5 do `drivers/kernelsu`; **vypnutie kprobe hookov**
   (`#ifdef CONFIG_KPROBES` → `#if defined(CONFIG_KPROBES) && 0`) — KSU ide cez Floppy manuálne hooky.
5. SUSFS→KSU patch `10_enable_susfs_for_ksu.patch` (na v0.9.5 = 0 rejectov).
6. [`scripts/fix_cred_rcu.py`](scripts/fix_cred_rcu.py) — Floppy má `cred.usage` = `atomic_long_t` → `atomic_long_inc_not_zero`.
7. defconfig: `CONFIG_KSU=y`, `CONFIG_KSU_SUSFS=y` + non-GKI bezpečná sada
   (bez `mnt_id_reorder`, bez `SUS_SU` — na non-GKI bootloopujú).
8. Build (`make O=out LLVM=1 LLVM_IAS=1`), sanity-check `.config`.
9. Zbal AnyKernel3 ([`anykernel/anykernel.sh`](anykernel/anykernel.sh), willow/ginkgo, `boot` partícia, A-only).
10. (Ak dané `stock_boot_url`) vyrob `new-boot.img` cez magiskboot.
11. Upload artefaktov + prerelease.

Lokálny build (čo som reálne pustil) je ten istý recept ručne cez WSL; výsledok je zip, ktorý máš.

### Prečo táto kombinácia (a prečo stock Floppy bootloopoval)

Pôvodný FloppyKernel KSU-Next+SUSFS na A17 bootloopoval pravdepodobne preto, že KSU-Next `next`
vyžaduje `CONFIG_KPROBES` a kprobes hooky sa **sčítali** s Floppy manuálnymi `ksu_handle_*` hookmi
→ dvojité hookovanie. Tu je KSU v0.9.5 **bez kprobes**, len manuálne hooky → žiadne dvojité hookovanie.
