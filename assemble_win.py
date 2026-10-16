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
for whl in sorted(glob.glob("build/wheels/*.whl")):
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

# 3) proxy_tools solo existe como .tar.gz
for sdist in glob.glob("build/wheels/proxy_tools-*.tar.gz"):
    with tarfile.open(sdist) as t:
        for m in t.getmembers():
            if m.name.endswith("proxy_tools.py"):
                open(SP + "/proxy_tools.py", "wb").write(t.extractfile(m).read())

# 4) La aplicacion
shutil.copy("app/aven_pdf.py", BASE + "/app/aven_pdf.py")
shutil.copy("app/aven.ico", BASE + "/app/aven.ico")
print("payload listo:", count, "ruedas integradas")
