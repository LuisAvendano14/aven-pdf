"""Arma el payload de Aven PDF en el runner de Windows:
Python incrustado + librerias integradas + la app. Sin internet en destino."""
import zipfile, tarfile, os, shutil, glob

import base64 as _b64
if not os.path.exists("app/aven.ico") and os.path.exists("app/aven_ico_b64.txt"):
    open("app/aven.ico", "wb").write(_b64.b64decode(open("app/aven_ico_b64.txt").read()))

BASE = "build/payload"
shutil.rmtree("build/payload", ignore_errors=True)
os.makedirs(BASE + "/python", exist_ok=True)
os.makedirs(BASE + "/app", exist_ok=True)

# 1) Python incrustado oficial
with zipfile.ZipFile("build/python-embed.zip") as z:
    z.extractall(BASE + "/python")
open(BASE + "/python/python313._pth", "w").write(
    "python313.zip\n.\nLib\\site-packages\n..\\app\nimport site\n")

# 2) Ruedas -> site-packages (se omite opencv con GUI: basta el headless)
SP = BASE + "/python/Lib/site-packages"
os.makedirs(SP, exist_ok=True)
count = 0
# Dos candados contra paquetes rotos en el payload:
# (a) Si la carpeta trae DOS versiones del mismo paquete, integrar AMBAS
#     sobrepone sus archivos y el paquete queda roto (pasó con Pillow).
#     Se integra solo la versión mayor de cada paquete.
# (b) El Python incrustado del paquete es 3.13: solo sirven ruedas cp313,
#     abi3 o universales. Una rueda de OTRO Python (p. ej. cp314, si el
#     python del runner cambió) se ve igual pero el programa no la puede
#     cargar: es el error «cannot import name '_imaging'».
def _rueda_info(nombre):
    partes = nombre[:-4].split("-")
    return partes[0].lower(), (partes[1] if len(partes) > 1 else "0")

def _version_tupla(v):
    nums = []
    for trozo in v.replace("+", ".").split("."):
        dig = ""
        for ch in trozo:
            if ch.isdigit(): dig += ch
            else: break
        nums.append(int(dig) if dig else 0)
    return tuple(nums)

import re as _re
def _compatible(nombre):
    low = nombre.lower()
    if "abi3" in low or "none-any" in low or "py2.py3" in low:
        return True
    if "cp313" in low:
        return True
    if _re.search(r"cp3\d+", low):
        return False
    return True

_elegidas = {}
for _whl in glob.glob("build/wheels/*.whl"):
    _nombre = os.path.basename(_whl)
    if not _compatible(_nombre):
        print("rueda omitida (es de otro Python):", _nombre)
        continue
    _dist, _ver = _rueda_info(_nombre)
    if _dist not in _elegidas or _version_tupla(_ver) > _version_tupla(_rueda_info(os.path.basename(_elegidas[_dist]))[1]):
        _elegidas[_dist] = _whl

for whl in sorted(_elegidas.values()):
    nombre = os.path.basename(whl)
    if nombre.startswith("opencv_python-"):
        continue
    with zipfile.ZipFile(whl) as z:
        for name in z.namelist():
            parts = name.split("/")
            if ".data" in parts:
                i = parts.index(".data")
                kind = parts[i + 1] if len(parts) > i + 1 else ""
                if kind in ("purelib", "platlib"):
                    name2 = "/".join(parts[i + 2:])
                    if not name2:
                        continue
                    target = os.path.join(SP, name2)
                else:
                    continue
            else:
                target = os.path.join(SP, name)
            if name.endswith("/"):
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(name) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    count += 1

# Control de cordura: el núcleo compilado de Pillow para cp313 debe estar
# dentro del paquete; si no está, las ruedas se descargaron para otro
# Python y todo lo que usa PIL fallaría en la PC del usuario.
if not any("cp313" in os.path.basename(p) for p in glob.glob(SP + "/PIL/_imaging*.pyd")):
    raise SystemExit("ERROR: falta PIL/_imaging para cp313 en el paquete: las ruedas se descargaron para otro Python (corregir el paso de descarga del workflow)")

# 3) proxy_tools solo existe como .tar.gz
for sdist in glob.glob("build/wheels/proxy_tools-*.tar.gz"):
    with tarfile.open(sdist) as t:
        for m in t.getmembers():
            if m.name.endswith("proxy_tools.py"):
                open(SP + "/proxy_tools.py", "wb").write(t.extractfile(m).read())

# 3.5) Runtime de Visual C++ junto al programa: onnxruntime (OCR) lo
# necesita y no toda PC lo trae; sin el, el OCR muere con "DLL load failed".
sys32 = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32")
for dll in ("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll", "concrt140.dll"):
    src = os.path.join(sys32, dll)
    if os.path.exists(src):
        shutil.copy(src, BASE + "/python/" + dll)
        capi = os.path.join(SP, "onnxruntime", "capi")
        if os.path.isdir(capi):
            shutil.copy(src, os.path.join(capi, dll))

# 4) La aplicacion
shutil.copy("app/aven_pdf.py", BASE + "/app/aven_pdf.py")
shutil.copy("app/aven_ui.py", BASE + "/app/aven_ui.py")
shutil.copy("app/aven.ico", BASE + "/app/aven.ico")

# 5) Verificación DENTRO del paquete ya armado, con el Python del paquete:
# Pillow debe importar y funcionar (su parte Python y su núcleo compilado
# deben ser de la MISMA versión; mezclados, importar Image revienta) y
# PyMuPDF debe abrir un documento. Si algo está roto, la compilación FALLA
# aquí con un mensaje claro, en vez de entregar un instalador que falla en
# silencio en la PC del usuario.
import subprocess
_exe = os.path.join(BASE, "python", "python.exe")
if os.path.exists(_exe):
    _pruebas = [
        ("Pillow", "import os, tempfile, PIL; from PIL import Image; "
                   "p = os.path.join(tempfile.gettempdir(), 'aven_pil_test.png'); "
                   "Image.new('RGB', (8, 8), (255, 0, 0)).save(p); os.remove(p); "
                   "print('Pillow OK', PIL.__version__)"),
        ("PyMuPDF", "import pymupdf; d = pymupdf.open(); d.new_page(); "
                    "print('PyMuPDF OK', getattr(pymupdf, '__version__', ''))"),
        ("onnxruntime", "import onnxruntime; "
                        "print('onnxruntime OK', onnxruntime.__version__)"),
    ]
    for _nombre_p, _codigo in _pruebas:
        _r = subprocess.run([_exe, "-c", _codigo], capture_output=True, text=True)
        print((_r.stdout or "").strip())
        if _r.returncode != 0:
            print(_r.stderr)
            raise SystemExit("ERROR: " + _nombre_p + " quedo roto en el paquete; compilacion detenida a proposito")
print("payload listo:", count, "ruedas integradas")
