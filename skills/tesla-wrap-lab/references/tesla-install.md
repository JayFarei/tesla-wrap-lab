# Install a wrap on the Tesla display

These are digital Paint Shop skins, not physical vinyl files. Source: https://github.com/teslamotors/custom-wraps, verified 2026-10-01. Check the current official instructions if the user's app or vehicle UI differs.

1. Download the PNG for the exact vehicle template. Use the generated filename; do not copy a wrap made for a different Model Y body.
2. Tesla app v4.59.0 or later: **Creations → Wrap → Upload**, and choose the PNG. Alternatively, use a compatible USB drive with a folder named exactly **Wraps** at its root; place the PNG inside it.
3. In the vehicle, open **Toybox → Paint Shop → Wraps** and select the design. Inspect all sides and report any distortion for the next iteration.

The official limits are PNG, 512×512 to 1024×1024 pixels, no larger than 1 MB, filenames using alphanumeric characters/underscores/dashes/spaces, maximum 30 characters; up to 10 wraps from the app and 10 from USB. This repository uses 1024 square, ≤1,000,000 bytes and a conservative 30-character filename including extension.

USB formats: exFAT, FAT32, MS-DOS FAT, ext3 or ext4. NTFS is not supported. The drive must not contain map or firmware updates. Do not format an existing drive or overwrite its data as part of ordinary wrap creation. If the user explicitly asks for a copy, verify the destination and use a non-destructive file copy; do not erase or repartition it.

If the Wraps menu is missing, verify app/vehicle software support rather than promising the wrap will install. Do not invent a universal firmware requirement or claim successful installation until the user confirms it. Matte preview settings, environment lighting and camera position are not included in the PNG.
