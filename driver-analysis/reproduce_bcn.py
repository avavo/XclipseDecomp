"""Reproduz a analise BCn/ELF usada no bundle (Windows + Linux).

Uso:
    python reproduce_bcn.py [caminho/vulkan.samsung.so]

Padrao: ../radv/vendor/vulkan.samsung.so (quando cwd = xclipse940-privado).
Saida: contagens + veredito BC1-7 + checagens do repo externo.
"""
import re
import struct
import sys
from pathlib import Path

def load(p: Path) -> bytes:
    return p.read_bytes()

def strings(data: bytes, n: int = 4):
    return [m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{%d,}' % n, data)]

def main() -> int:
    so = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / ".." / "radv" / "vendor" / "vulkan.samsung.so"
    # quando o bundle esta em Documents\xclipse940-privado, o default acima resolve para Documents\radv
    alt = Path(r"C:\Users\alvaro\Documents\radv\vendor\vulkan.samsung.so")
    if not so.exists() and alt.exists():
        so = alt
    if not so.exists():
        print(f"NAO ACHEI: {so}")
        print("Passe o caminho: python reproduce_bcn.py C:\\Users\\alvaro\\Documents\\radv\\vendor\\vulkan.samsung.so")
        return 2
    data = load(so)
    print(f"alvo: {so} ({len(data)} bytes)")
    strs = strings(data)
    print(f"strings(>=4): {len(strs)}")
    sset = set(strs)

    vkbc = sorted(s for s in sset if s.startswith("VK_FORMAT_BC"))
    bc = sorted(s for s in sset if re.fullmatch(r"Bc[0-9]_.*", s))
    img = sorted(s for s in sset if s.startswith("IMG_FMT_"))
    img_bc = [s for s in img if "_BC" in s]
    print(f"VK_FORMAT_BC*: {len(vkbc)} -> {vkbc}")
    print(f"Bc*: {len(bc)} -> {bc}")
    print(f"IMG_FMT total: {len(img)}; com _BC: {len(img_bc)} -> {img_bc}")

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
    # .dynsym
    try:
        e_shoff = struct.unpack("<Q", data[0x28:0x30])[0]
        e_shentsize = struct.unpack("<H", data[0x3A:0x3C])[0]
        e_shnum = struct.unpack("<H", data[0x3C:0x3E])[0]
        e_shstrndx = struct.unpack("<H", data[0x3E:0x40])[0]
        secs = [struct.unpack("<IIQQQQIIQQ", data[e_shoff + i * e_shentsize:e_shoff + (i + 1) * e_shentsize]) for i in range(e_shnum)]
        shstr_off, shstr_sz = secs[e_shstrndx][4], secs[e_shstrndx][5]
        shstr = data[shstr_off:shstr_off + shstr_sz]
        def nm(i):
            e = shstr.find(b"\x00", i)
            return shstr[i:e].decode()
        for (n, t, fl, a, off, sz, lnk, inf, al, esz) in secs:
            if nm(n) == ".dynsym":
                print(f".dynsym: {sz // esz} entradas")
    except Exception as e:  # noqa: BLE001
        print(f".dynsym: falha ao parsear ({e})")

    ok_bcn = (len(vkbc) == 16 and len([s for s in img_bc if "BC4" in s or "BC5" in s or "BC6" in s or "BC7" in s]) == 0)
    print("VEREDITO ESTATICO:", "BC1-3 completos; BC4-7 incompletos (sem IMG_FMT)" if ok_bcn else "diverge do build SM-S926B de referencia - investigar")
    print("OBS: estatico != runtime. Confirmar com vkGetPhysicalDeviceFeatures/FormatProperties no aparelho.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
