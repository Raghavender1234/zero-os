#!/usr/bin/env python3
"""
ZeroOS Samsung Galaxy A15 Image Packager
Packages system.img into:
1. Odin Flashable Tar: ZeroOS_A15_Odin.tar (for flashing in Odin AP slot)
2. DSU Sideloader Package: ZeroOS_A15_DSU.img.gz (for dual-boot without Knox trip)
"""

import os
import sys
import tarfile
import gzip
import shutil

def package_a15(system_img_path, output_dir):
    if not os.path.exists(system_img_path):
        print(f"Error: {system_img_path} not found.")
        print("Please build system.img first or provide the path to your compiled image.")
        return False

    os.makedirs(output_dir, exist_ok=True)
    img_size_mb = os.path.getsize(system_img_path) / (1024 * 1024)
    print(f"Input image: {system_img_path} ({img_size_mb:.1f} MB)")

    # 1. Package for Odin (tar format with system.img inside)
    odin_tar = os.path.join(output_dir, "ZeroOS_GalaxyA15_Odin.tar")
    print(f"Generating Odin flashable package: {odin_tar} ...")
    with tarfile.open(odin_tar, "w") as tar:
        tar.add(system_img_path, arcname="system.img")
    print(f"✓ Odin package ready: {odin_tar}")

    # 2. Package for DSU Sideloader (gzip compressed for seamless phone installation)
    dsu_gz = os.path.join(output_dir, "ZeroOS_GalaxyA15_DSU.img.gz")
    print(f"Generating DSU Sideloader package: {dsu_gz} ...")
    with open(system_img_path, 'rb') as f_in:
        with gzip.open(dsu_gz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"✓ DSU Sideloader package ready: {dsu_gz}")

    print("\n=======================================================")
    print("Galaxy A15 Flashing Options:")
    print("1. ZERO-RISK TEST (Recommended):")
    print(f"   Transfer '{os.path.basename(dsu_gz)}' to phone.")
    print("   Open DSU Sideloader -> Select file -> Install -> Reboot.")
    print("   Does NOT trip Knox (0x0 preserved), does NOT wipe stock One UI.")
    print("")
    print("2. PERMANENT ODIN FLASH (Global/Exynos SM-A155F/SM-A156B only):")
    print(f"   Put phone in Download Mode -> Select '{os.path.basename(odin_tar)}' in Odin AP slot.")
    print("=======================================================")
    return True

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_img = os.path.join(root, 'out', 'target', 'product', 'zero_arm64', 'system.img')
    out_dir = os.path.join(root, 'out', 'samsung_a15')

    target_img = sys.argv[1] if len(sys.argv) > 1 else default_img
    if not os.path.exists(target_img):
        # Create dummy for testing if not yet compiled locally
        print(f"Note: Local compiled image not yet found at {target_img}.")
        print("Creating build-ready output directory at out/samsung_a15/")
        os.makedirs(out_dir, exist_ok=True)
    else:
        package_a15(target_img, out_dir)
