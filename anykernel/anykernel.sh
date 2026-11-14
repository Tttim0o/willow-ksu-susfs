# AnyKernel3 willow (Redmi Note 8T) / ginkgo (Redmi Note 8) - SM6125
# Tento subor CI skopiruje cez osm0sis/AnyKernel3, aby bol zip spravne device-cieleny.

properties() { '
kernel.string=willow KSU-Next + SUSFS (PixelOS 17) by ttt
do.devicecheck=1
do.modules=0
do.systemless=1
do.cleanup=1
do.cleanuponabort=1
device.name1=willow
device.name2=ginkgo
device.name3=
device.name4=
device.name5=
supported.versions=
supported.patchlevels=
'; }

block=/dev/block/bootdevice/by-name/boot;
is_slot_device=0;
ramdisk_compression=auto;
patch_vbmeta_flag=auto;

. tools/ak3-core.sh;

split_boot;

# willow/ginkgo: boot image header v2 ma dtb vo vnutri. Ak je v zipe nas dtb, nahradime ho,
# inak ponechame z boot.imgu. Image.gz je samotny kernel.
if [ -f $home/dtb ]; then
  flash_boot dtb;
else
  flash_boot;
fi
