"""Static BCn/ELF checks for Samsung's Xclipse Vulkan driver.

Usage:
    python reproduce_bcn.py <path/to/vulkan.samsung.so>

Pull the driver from your own device first, e.g.:
    adb pull /vendor/lib64/hw/vulkan.samsung.so

Output: BC1-BC7 name counts, PAL IMG_FMT coverage, and the key
presence/absence checks behind driver-analysis/BCN_BC1-BC7.md.
"""
import re
import struct
import sys
from pathlib import Path


def strings(data: bytes, n: int = 4):
    return [m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{%d,}' % n, data)]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python reproduce_bcn.py <path/to/vulkan.samsung.so>")
        return 2
    so = Path(sys.argv[1])
    if not so.exists():
        print(f"Not found: {so}")
        return 2
    data = so.read_bytes()
    print(f"target: {so} ({len(data)} bytes)")
    strs = strings(data)
    print(f"strings(>=4): {len(strs)}")
    sset = set(strs)

    vkbc = sorted(s for s in sset if s.startswith("VK_FORMAT_BC"))
    bc = sorted(s for s in sset if re.fullmatch(r"Bc[0-9]_.*", s))
    img = sorted(s for s in sset if s.startswith("IMG_FMT_"))
    img_bc = [s for s in img if "_BC" in s]
    print(f"VK_FORMAT_BC*: {len(vkbc)} -> {vkbc}")
    print(f"Bc*: {len(bc)} -> {bc}")
    print(f"IMG_FMT total: {len(img)}; with _BC: {len(img_bc)} -> {img_bc}")

    checks = {
        "textureCompressionBC": data.count(b"textureCompressionBC"),
        "FormatPropertiesTable": data.count(b"FormatPropertiesTable"),
        "GetFormatFlags": data.count(b"GetFormatFlags"),
        "formatId": data.count(b"formatId"),
        "sgpu_query_soc_info": data.count(b"sgpu_query_soc_info"),
        "sgpu_instance_data_destroy": data.count(b"sgpu_instance_data_destroy"),
        "IMG_FMT_BC4": data.count(b"IMG_FMT_BC4"),
        "IMG_FMT_BC7": data.count(b"IMG_FMT_BC7"),
        "GFX405": data.count(b"GFX405"),
    }
    for k, v in checks.items():
        print(f"{k}: {v}")
    # mov w1, 0xdb48 = bytes 01 69 9B 52 (LE)
    print("mov_w1_0xdb48:", data.count(bytes.fromhex("01 69 9B 52")))
    # .dynsym entry count
    try:
        e_shoff = struct.unpack("<Q", data[0x28:0x30])[0]
        e_shentsize = struct.unpack("<H", data[0x3A:0x3C])[0]
        e_shnum = struct.unpack("<H", data[0x3C:0x3E])[0]
        e_shstrndx = struct.unpack("<H", data[0x3E:0x40])[0]
        secs = [struct.unpack("<IIQQQQIIQQ", data[e_shoff + i * e_shentsize:e_shoff + (i + 1) * e_shentsize]) for i in range(e_shnum)]
        shstr_off, shstr_sz = secs[e_shstrndx][4], secs[e_shstrndx][5]
        shstr = data[shstr_off:shstr_off + shstr_sz]

        def secname(i):
            e = shstr.find(b"\x00", i)
            return shstr[i:e].decode()

        for (n, _t, _fl, _a, _off, sz, _lnk, _inf, _al, esz) in secs:
            if secname(n) == ".dynsym":
                print(f".dynsym: {sz // esz} entries")
    except Exception as e:  # noqa: BLE001
        print(f".dynsym: parse failed ({e})")

    incomplete = [s for s in img_bc if "BC4" in s or "BC5" in s or "BC6" in s or "BC7" in s]
    if len(vkbc) == 16 and not incomplete:
        print("STATIC VERDICT: BC1-3 complete; BC4-7 incomplete (no IMG_FMT)")
    else:
        print("STATIC VERDICT: differs from the reference SM-S926B build - investigate")
    print("NOTE: static != runtime. Confirm with vkGetPhysicalDeviceFeatures/FormatProperties on-device.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
