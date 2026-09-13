"""Static BCn/ELF checks for Samsung's Xclipse Vulkan driver.

Usage:
    python reproduce_bcn.py <path/to/vulkan.samsung.so> [--disasm]

Pull the driver from your own device first, e.g.:
    adb pull /vendor/lib64/hw/vulkan.samsung.so

Output: BC1-BC7 name counts, PAL IMG_FMT coverage, and the key
presence/absence checks behind driver-analysis/BCN_BC1-BC7.md.
With --disasm (requires the `capstone` package): disassembles .text for
stores to the BC feature slot (struct offset 88) with sibling-offset
clustering, as described in the Disassembly section of BCN_BC1-BC7.md.
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
        "ForceEtcAstcEnable": data.count(b"ForceEtcAstcEnable"),
        "disables BC4-7": data.count(b"disables BC4-7"),
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
    if len(vkbc) == 16 and not incomplete and data.count(b"ForceEtcAstcEnable") > 0:
        print("STATIC VERDICT: BC1-7 reported by default (opt-out off); PAL IMG_FMT_BC4-7 names absent (incomplete)")
    else:
        print("STATIC VERDICT: differs from the reference SM-S926B build - investigate")
    print("NOTE: static != runtime. Confirm with vkGetPhysicalDeviceFeatures/FormatProperties on-device.")
    if "--disasm" in sys.argv[2:]:
        disasm_scan(data, secs)
    return 0


def disasm_scan(data: bytes, secs) -> None:
    """Hunt stores to struct offset 88 (BC feature slot) in .text."""
    try:
        from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
    except ImportError:
        print("disasm: capstone not installed (pip install capstone)")
        return
    t_off = t_sz = t_va = None
    # largest executable PROGBITS section (.text)
    for (n, t, fl, addr, off, sz, _lnk, _inf, _al, _esz) in secs:
        if t == 1 and (fl & 0x4) and (t_off is None or sz > t_sz):
            t_off, t_sz, t_va = off, sz, addr
    if t_off is None:
        print("disasm: no executable section found")
        return
    seg = data[t_off:t_off + t_sz]
    sites = []
    for m in re.finditer(rb"(?=(.[\x58-\x5b]\x00\xb9))", seg):
        o = m.start()
        if (t_off + o) % 4 != 0:
            continue
        w = struct.unpack("<I", seg[o:o + 4])[0]
        if (w & 0xBFC00000) == 0xB9000000 and ((w >> 10) & 0xFFF) == 22:
            sites.append(o)
    print(f"disasm: STR W,#88 sites: {len(sites)}")
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    clusters = 0
    for o in sites:
        lo = max(0, o - 512)
        insns = list(md.disasm(seg[lo:o + 512], t_va + lo))
        idx = {ins.address: i for i, ins in enumerate(insns)}
        site_va = t_va + o
        if site_va not in idx:
            continue
        si = idx[site_va]
        site_op = insns[si].op_str
        base = site_op.split("[", 1)[1].split(",")[0].strip()
        offs = set()
        for ins in insns:
            if ins.mnemonic == "str" and ins.op_str.startswith("w"):
                mem = ins.op_str.split("[", 1)[1] if "[" in ins.op_str else ""
                mm = re.match(r"\s*(x\d+)(?:\s*,\s*#?(0x[0-9a-f]+|\d+))?", mem)
                if mm and mm.group(1) == base and mm.group(2) is not None:
                    offs.add(int(mm.group(2), 0))
        if {80, 84, 88} <= offs:
            clusters += 1
            print(f"disasm: cluster base={base} va={site_va:#x} offsets={sorted(o for o in offs if 64 <= o <= 120)}")
    print(f"disasm: {clusters} sibling-cluster sites (see BCN_BC1-BC7.md for analysis)")


if __name__ == "__main__":
    raise SystemExit(main())
