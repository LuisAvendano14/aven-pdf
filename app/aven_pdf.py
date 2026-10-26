# -*- coding: utf-8 -*-
"""
Aven PDF v7 — editor de PDF local, construido con código propio siguiendo el
mapa de funciones obtenido con REA de Nitro PDF Pro 26 (módulos np_*).
Corre en la laptop del usuario, sin administrador, sin internet:
    python aven_pdf.py   ->  http://127.0.0.1:8899
Dependencias: pypdf, pymupdf (pip install --user pypdf pymupdf)
"""
import base64, io, json, zipfile, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pymupdf
from pypdf import PdfReader, PdfWriter

PORT = 8899

def b64d(s): return base64.b64decode(s)
def b64e(b): return base64.b64encode(b).decode()

def P(d):
    """Bytes del PDF del pedido. Si vino por doc_id, el despachador ya dejo
    los bytes crudos en d['_raw']: antes CADA llamada (cada pagina dibujada)
    volvia a codificar el archivo entero a base64 solo para decodificarlo."""
    raw = d.get("_raw")
    if raw is not None: return raw
    return b64d(d["pdf"])

def parse_pages(spec, total):
    """'1-3,5' -> [0,1,2,4] (índices 0-based, sin duplicados, en orden)."""
    out = []
    for part in (spec or "").split(","):
        part = part.strip()
        if not part: continue
        if "-" in part:
            a, b = part.split("-", 1)
            try: rng = range(int(a), int(b) + 1)
            except ValueError: raise ValueError("Páginas no válidas: usa números y rangos como 1-3,5")
            if int(b) < int(a):
                raise ValueError("Rango invertido: " + part + " (la página final no puede ser menor que la inicial)")
        else:
            try: rng = [int(part)]
            except ValueError: raise ValueError("Páginas no válidas: usa números y rangos como 1-3,5")
        for n in rng:
            if 1 <= n <= total and (n - 1) not in out:
                out.append(n - 1)
    return out

def api_info(d):
    data = P(d)
    try: doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception: raise ValueError("El archivo no es un PDF válido o está dañado")
    if doc.is_encrypted and not doc.authenticate(d.get("password") or ""):
        raise ValueError("El PDF está protegido con contraseña: se te pedirá en una ventana al abrirlo")
    md = doc.metadata or {}
    return {"pages": doc.page_count, "encrypted": doc.is_encrypted,
            "title": md.get("title") or "", "author": md.get("author") or "",
            "creator": md.get("creator") or "", "producer": md.get("producer") or "",
            "size_kb": round(len(data) / 1024, 1),
            "page_sizes": [[round(p.rect.width), round(p.rect.height)] for p in doc],
            "bookmarks": len(doc.get_toc()),
            "toc": [[lv, t, pg] for (lv, t, pg) in doc.get_toc()]}


# ===== Almacén de documentos (1.7): el cliente sube el PDF una sola vez y
# después todo viaja con un doc_id corto. Sin esto, CADA página dibujada
# volvía a subir el archivo entero (un PDF de 31 MB = minutos por cambio).
import threading, uuid, time
from collections import OrderedDict
DOCS = OrderedDict()
DOCS_LOCK = threading.Lock()
DOCS_MAX_BYTES = 600 * 1024 * 1024

def store_doc(data):
    did = uuid.uuid4().hex[:12]
    with DOCS_LOCK:
        DOCS[did] = data
        total = sum(len(v) for v in DOCS.values())
        while (total > DOCS_MAX_BYTES or len(DOCS) > 40) and len(DOCS) > 1:
            _, old = DOCS.popitem(last=False)
            total -= len(old)
    return did

RENDER_CACHE = OrderedDict()
RENDER_CACHE_BYTES = [0]
RENDER_CACHE_MAX_BYTES = 150 * 1024 * 1024
RENDER_LOCK = threading.Lock()

def api_open(d):
    """Registra el PDF en el almacén y devuelve su info + doc_id."""
    data = P(d)
    info = api_info(d)
    info["doc_id"] = store_doc(data)
    return info

def api_fetch_doc(d):
    """Devuelve el PDF guardado bajo un doc_id (lo usa Deshacer/Rehacer,
    que ya no guarda copias enteras del archivo en la ventana)."""
    with DOCS_LOCK:
        data = DOCS.get(d.get("doc_id") or "")
    if data is None:
        raise ValueError("El documento ya no está en la memoria del programa (se abrieron otros después).")
    return {"pdf": b64e(data)}

def api_render(d):
    _ckey = None
    if d.get("doc_id"):
        _ckey = (d["doc_id"], int(d.get("page", 0)),
                 round(float(d.get("zoom", 1.4)), 3), d.get("password") or "")
        with RENDER_LOCK:
            _hit = RENDER_CACHE.get(_ckey)
            if _hit is not None:
                RENDER_CACHE.move_to_end(_ckey)
                return dict(_hit)
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    if doc.is_encrypted and not doc.authenticate(d.get("password") or ""):
        raise ValueError("El PDF está protegido: escribe su contraseña en Acceso (pestaña Archivo)")
    _pno = int(d.get("page", 0))
    if not 0 <= _pno < doc.page_count:
        raise ValueError("La página %d no existe: el documento tiene %d páginas" % (_pno + 1, doc.page_count))
    page = doc[_pno]
    zoom = float(d.get("zoom", 1.4))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    out = {"png": b64e(pix.tobytes("png")), "pages": doc.page_count,
           "w": pix.width, "h": pix.height}
    if _ckey:
        with RENDER_LOCK:
            _old = RENDER_CACHE.get(_ckey)
            if _old is not None: RENDER_CACHE_BYTES[0] -= len(_old["png"])
            RENDER_CACHE[_ckey] = out
            RENDER_CACHE_BYTES[0] += len(out["png"])
            while RENDER_CACHE_BYTES[0] > RENDER_CACHE_MAX_BYTES and len(RENDER_CACHE) > 1:
                _k, _v = RENDER_CACHE.popitem(last=False)
                RENDER_CACHE_BYTES[0] -= len(_v["png"])
    return out

def api_merge(d):
    w = PdfWriter()
    for _k, item in enumerate(d["pdfs"], 1):
        r = PdfReader(io.BytesIO(b64d(item)))
        for p in r.pages: w.add_page(p)
        if d.get("_prog"): d["_prog"](_k * 100 // max(1, len(d["pdfs"])))
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_extract(d):
    r = PdfReader(io.BytesIO(P(d)))
    idx = parse_pages(d.get("pages", ""), len(r.pages))
    if not idx: raise ValueError("Indica páginas, p. ej. 1-3,5")
    w = PdfWriter()
    for i in idx: w.add_page(r.pages[i])
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_split_each(d):
    r = PdfReader(io.BytesIO(P(d)))
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for i, p in enumerate(r.pages, 1):
            w = PdfWriter(); w.add_page(p)
            b = io.BytesIO(); w.write(b)
            z.writestr(f"pagina_{i:03d}.pdf", b.getvalue())
    return {"zip": b64e(zbuf.getvalue()), "pages": len(r.pages)}

def api_split(d):
    r = PdfReader(io.BytesIO(P(d)))
    total = len(r.pages)
    parts = []
    if d.get("mode") == "ranges":
        spec = (d.get("spec") or "").strip()
        if not spec: raise ValueError("Escribe los rangos, p. ej. 1-3, 5-6")
        toks = [t.strip() for t in spec.split(",") if t.strip()]
        for k, t in enumerate(toks, 1):
            idx = parse_pages(t, total)
            if not idx: raise ValueError("Rango no válido: " + t)
            parts.append((f"parte_{k:02d}_pag_{t.replace('-', '_a_')}.pdf", idx))
    else:
        try: n = int(d.get("n", 1))
        except Exception: raise ValueError("El tamaño de parte debe ser un número")
        if n < 1: raise ValueError("El tamaño de parte debe ser 1 o más")
        for k, i in enumerate(range(0, total, n), 1):
            g = list(range(i, min(i + n, total)))
            a, b = g[0] + 1, g[-1] + 1
            nm = f"parte_{k:02d}_pag_{a}.pdf" if a == b else f"parte_{k:02d}_pag_{a}_a_{b}.pdf"
            parts.append((nm, g))
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for _k, (nm, idx) in enumerate(parts, 1):
            w = PdfWriter()
            for i in idx: w.add_page(r.pages[i])
            b = io.BytesIO(); w.write(b)
            z.writestr(nm, b.getvalue())
            if d.get("_prog"): d["_prog"](_k * 100 // max(1, len(parts)))
    return {"zip": b64e(zbuf.getvalue()), "parts": len(parts)}

def _open_tol(d):
    """Abre el PDF y lo autentica con la contraseña del pedido. Si sigue
    protegido, el error sale en español claro (antes pymupdf soltaba
    «File has not been decrypted» en inglés)."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password", "")) <= 0:
        raise ValueError("El PDF está protegido con contraseña: escríbela en el campo de Acceso (pestaña Archivo) y vuelve a intentarlo.")
    return doc

def api_rotate(d):
    # Con pymupdf (motor nativo): en archivos pesados tarda una fracción
    # de lo que tardaba pypdf reescribiendo el documento en Python puro.
    doc = _open_tol(d)
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    deg = int(d.get("degrees", 90))
    for i in idx:
        doc[i].set_rotation((doc[i].rotation + deg) % 360)
    return {"pdf": b64e(doc.tobytes()), "pages": doc.page_count}

def api_delete_pages(d):
    doc = _open_tol(d)
    drop = set(parse_pages(d.get("pages", ""), doc.page_count))
    if not drop: raise ValueError("Indica qué páginas borrar")
    if len(drop) >= doc.page_count: raise ValueError("No puedes borrar todas las páginas")
    doc.select([i for i in range(doc.page_count) if i not in drop])
    return {"pdf": b64e(doc.tobytes()), "pages": doc.page_count}

def api_watermark(d):
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    text = d.get("text") or "Aven PDF"
    for _pi, page in enumerate(doc):
        r = page.rect
        fs = max(28, r.width / max(6, len(text)) * 1.1)
        op = float(d.get("opacity", 0.25))
        pt = pymupdf.Point(r.width * 0.08, r.height * 0.55)
        page.insert_text(pt, text,
                         fontsize=fs, fontname="helv", color=(0.55, 0.6, 0.7),
                         fill_opacity=op, stroke_opacity=op,
                         morph=(pt, pymupdf.Matrix(35)))
        if d.get("_prog"): d["_prog"]((_pi + 1) * 100 // max(1, doc.page_count))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_add_text(d):
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    text = d.get("text") or ""
    size = float(d.get("size", 14))
    targets = list(range(doc.page_count)) if d.get("all") else [int(d.get("page", 0))]
    for pno in targets:
        page = doc[pno]
        r = page.rect
        x = r.width * float(d.get("x_pct", 10)) / 100.0
        y = r.height * float(d.get("y_pct", 12)) / 100.0
        align = d.get("align", "l")
        if align in ("c", "r") and text:
            tw = pymupdf.get_text_length(text, fontname="helv", fontsize=size)
            x = x - tw / 2.0 if align == "c" else x - tw
            if tw < r.width - 8:
                x = max(4, min(x, r.width - tw - 4))
            else:
                x = 4
        page.insert_text((x, y), text, fontsize=size,
                         fontname="helv", color=(0.05, 0.1, 0.25))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_watermark_image(d):
    """Marca de agua con imagen (logo/sello), centrada, en todas las páginas."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    img = b64d(d["image"])
    pix = pymupdf.Pixmap(img)
    iw, ih = pix.width, pix.height
    op = float(d.get("opacity", 0.25))
    if op < 1.0:
        # la transparencia va horneada en la imagen (set_alpha), porque
        # insert_image no acepta opacidad en todas las versiones
        if not pix.alpha:
            pix = pymupdf.Pixmap(pix, 1)
        src = pix.samples
        plane = src[pix.n - 1::pix.n]
        pix.set_alpha(bytes(int(b * op) for b in plane))
        img = pix.tobytes("png")
    wpct = float(d.get("width_pct", 55))
    for _pi, page in enumerate(doc):
        r = page.rect
        w = r.width * wpct / 100.0
        h = w * ih / float(iw)
        if h > r.height * 0.8:
            h = r.height * 0.8
            w = h * iw / float(ih)
        rect = pymupdf.Rect((r.width - w) / 2.0, (r.height - h) / 2.0,
                            (r.width + w) / 2.0, (r.height + h) / 2.0)
        page.insert_image(rect, stream=img, keep_proportion=False,
                          overlay=True)
        if d.get("_prog"): d["_prog"]((_pi + 1) * 100 // max(1, doc.page_count))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_stamp(d):
    """Sello de firma tipo np_signature_stamp: nombre + fecha, marco fino."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    page = doc[int(d.get("page", 0))]
    r = page.rect
    name = d.get("name") or "Firmado"
    fecha = datetime.date.today().isoformat()
    w, h = 260, 64
    x = r.width * float(d.get("x_pct", 55)) / 100.0
    y = r.height * float(d.get("y_pct", 82)) / 100.0
    rect = pymupdf.Rect(x, y, min(x + w, r.width - 10), y + h)
    page.draw_rect(rect, color=(0.1, 0.25, 0.6), width=1.2)
    page.insert_text((rect.x0 + 10, rect.y0 + 26), name, fontsize=15,
                     fontname="tiit", color=(0.1, 0.2, 0.45))
    page.insert_text((rect.x0 + 10, rect.y0 + 48), f"Firmado digitalmente · {fecha}",
                     fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_encrypt(d):
    if not (d.get("password") or ""):
        raise ValueError("Escribe la contraseña nueva para proteger el PDF")
    r = PdfReader(io.BytesIO(P(d)))
    w = PdfWriter()
    for p in r.pages: w.add_page(p)
    w.encrypt(d["password"], algorithm="AES-256")
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_decrypt(d):
    doc = _open_tol(d)
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_compress(d):
    data = P(d)
    doc = pymupdf.open(stream=data, filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password") or "") <= 0:
        raise ValueError("El PDF tiene contraseña: ábrelo primero con su contraseña.")
    dpi, calidad = {"pantalla": (150, 58), "media": (200, 74),
                    "alta": (300, 88)}.get(d.get("level"), (200, 74))
    # Ancho en pixeles que necesita cada imagen según el tamaño al que se
    # muestra en su página (una foto gigante mostrada chica sobra en pixeles).
    need = {}
    pages_of = {}
    for _pno, page in enumerate(doc):
        for img in page.get_images(full=True):
            xref = img[0]
            for r in page.get_image_rects(xref):
                px = r.width / 72.0 * dpi
                if px > need.get(xref, 0): need[xref] = px
                pages_of.setdefault(xref, set()).add(_pno)
    from PIL import Image
    hechas = 0
    _tot = max(1, len(need)); _van = 0
    for xref, needpx in need.items():
        try:
            pix = pymupdf.Pixmap(doc, xref)
            if pix.width <= needpx * 1.05: continue      # ya es chica: no tocar
            if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
            if pix.n >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            if pix.n not in (1, 3): continue
            im = Image.frombytes("RGB" if pix.n == 3 else "L",
                                 (pix.width, pix.height), pix.samples)
            nw = max(1, round(needpx)); nh = max(1, round(pix.height * needpx / pix.width))
            im = im.resize((nw, nh), Image.LANCZOS)
            buf = io.BytesIO(); im.save(buf, "JPEG", quality=calidad)
            nuevo = buf.getvalue()
            for _pno in pages_of.get(xref, ()):
                doc[_pno].replace_image(xref, stream=nuevo)
            hechas += 1
            del pix, im, nuevo
            if hechas % 20 == 0:
                import gc; gc.collect()
        except Exception:
            continue
        _van += 1
        if d.get("_prog"): d["_prog"](_van * 100 // _tot)
    out = doc.tobytes(garbage=4, deflate=True)
    return {"pdf": b64e(out), "pages": doc.page_count, "images_done": hechas,
            "before_kb": round(len(data) / 1024, 1), "after_kb": round(len(out) / 1024, 1)}

def api_to_images(d):
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    zoom = float(d.get("zoom", 2.0))
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            z.writestr(f"pagina_{i:03d}.png", pix.tobytes("png"))
            if d.get("_prog"): d["_prog"](i * 100 // doc.page_count)
    return {"zip": b64e(zbuf.getvalue()), "pages": doc.page_count}

def api_to_text(d):
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    parts = []
    for i, page in enumerate(doc, 1):
        parts.append(f"===== Página {i} =====\n" + page.get_text())
        if d.get("_prog"): d["_prog"](i * 100 // max(1, doc.page_count))
    return {"text": "\n\n".join(parts), "pages": doc.page_count}

def api_images_to_pdf(d):
    doc = pymupdf.open()
    for _k, item in enumerate(d["images"], 1):
        img = b64d(item)
        pix = pymupdf.Pixmap(img)
        page = doc.new_page(width=pix.width, height=pix.height)
        page.insert_image(pymupdf.Rect(0, 0, pix.width, pix.height), stream=img)
        if d.get("_prog"): d["_prog"](_k * 100 // max(1, len(d["images"])))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_text_to_pdf(d):
    text = d.get("text") or ""
    title = d.get("title") or "Documento Aven PDF"
    doc = pymupdf.open()
    W, H, M, LH, FS = 595, 842, 56, 15.5, 11.5
    lines = []
    for raw in text.split("\n"):
        s = raw
        while len(s) > 92:
            cut = s.rfind(" ", 0, 92)
            if cut < 20: cut = 92
            lines.append(s[:cut]); s = s[cut:].lstrip()
        lines.append(s)
    per = int((H - 2 * M) / LH)
    for start in range(0, max(len(lines), 1), per):
        page = doc.new_page(width=W, height=H)
        if start == 0:
            page.insert_text((M, M), title, fontsize=16, fontname="hebo", color=(0.05, 0.15, 0.4))
        y = M + (34 if start == 0 else 0)
        for ln in lines[start:start + per]:
            page.insert_text((M, y), ln, fontsize=FS, fontname="helv", color=(0.1, 0.1, 0.1))
            y += LH
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_form_fields(d):
    r = PdfReader(io.BytesIO(P(d)))
    f = r.get_fields() or {}
    return {"fields": [{"name": k, "type": str(v.get("/FT", "")), "value": str(v.get("/V", "") or "")}
                        for k, v in f.items()]}

def api_fill_form(d):
    r = PdfReader(io.BytesIO(P(d)))
    w = PdfWriter()
    w.append(r)
    vals = d.get("values") or {}
    for pno in range(len(w.pages)):
        try: w.update_page_form_field_values(w.pages[pno], vals, auto_regenerate=False)
        except Exception: pass
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

# ======================= v2: conversión, OCR, firma, edición =======================

def api_to_word(d):
    """PDF -> Word (.docx) intentando conservar el formato (motor pdf2docx)."""
    import tempfile, os
    from pdf2docx import Converter
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in.pdf"); dst = os.path.join(td, "out.docx")
        open(src, "wb").write(P(d))
        cv = Converter(src)
        try: cv.convert(dst, start=0, end=None, multi_processing=False)
        finally: cv.close()
        data = open(dst, "rb").read()
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    return {"file": b64e(data), "name": "convertido.docx", "pages": doc.page_count}

def api_to_excel(d):
    """PDF -> Excel (.xlsx): una hoja por página con las tablas detectadas."""
    import pdfplumber
    from openpyxl import Workbook
    wb = Workbook(); wb.remove(wb.active)
    total_tables = 0
    with pdfplumber.open(io.BytesIO(P(d))) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            ws = wb.create_sheet(f"Pag{i}")
            tables = page.extract_tables() or []
            row = 1
            if not tables:
                txt = page.extract_text() or ""
                for ln in txt.split("\n"):
                    ws.cell(row=row, column=1, value=ln); row += 1
            for t in tables:
                total_tables += 1
                for r in t:
                    for c, val in enumerate(r, 1):
                        ws.cell(row=row, column=c, value=(val or "").replace("\n", " "))
                    row += 1
                row += 1
            if d.get("_prog"): d["_prog"](i * 100 // max(1, len(pdf.pages)))
    if not wb.sheetnames: wb.create_sheet("Vacio")
    buf = io.BytesIO(); wb.save(buf)
    return {"file": b64e(buf.getvalue()), "name": "convertido.xlsx", "tables": total_tables}

_OCR_ENGINE = None
def _ocr():
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        try:
            import os, sys
            base = os.path.dirname(sys.executable)
            for cand in (base, os.path.join(base, "Lib", "site-packages", "onnxruntime", "capi")):
                try: os.add_dll_directory(cand)
                except Exception: pass
            from rapidocr_onnxruntime import RapidOCR
            _OCR_ENGINE = RapidOCR()
        except Exception:
            raise RuntimeError("El OCR no pudo arrancar en esta computadora: falta un componente de Windows (librerías de Visual C++). Todo lo demás de Aven PDF funciona normal; este aviso es solo para el OCR.")
    return _OCR_ENGINE

def _ocr_page(pix):
    import numpy as np
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4: img = img[:, :, :3]
    res, _ = _ocr()(img)
    return res or []

def api_ocr_text(d):
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    parts = []
    _van = 0
    for i in idx:
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(3, 3))
        lines = [t for (_b, t, _c) in _ocr_page(pix)]
        parts.append(f"===== Página {i+1} (OCR) =====\n" + "\n".join(lines))
        _van += 1
        if d.get("_prog"): d["_prog"](_van * 100 // max(1, len(idx)))
    return {"text": "\n\n".join(parts), "pages": len(idx)}

def api_ocr_pdf(d):
    """Crea un PDF buscable: imagen de la página + capa de texto invisible OCR."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    out = pymupdf.open()
    zoom = 3
    for _pi, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        res = _ocr_page(pix)
        np_ = out.new_page(width=page.rect.width, height=page.rect.height)
        np_.insert_image(np_.rect, stream=pix.tobytes("png"))
        for box, text, _conf in res:
            xs = [p[0] for p in box]; ys = [p[1] for p in box]
            x0, y0 = min(xs) / zoom, min(ys) / zoom
            h = (max(ys) - min(ys)) / zoom
            np_.insert_text((x0, y0 + h * 0.85), text, fontsize=max(5, h * 0.8),
                           fontname="helv", render_mode=3)
        if d.get("_prog"): d["_prog"]((_pi + 1) * 100 // doc.page_count)
    return {"pdf": b64e(out.tobytes(garbage=3, deflate=True)), "pages": out.page_count}

def api_replace_text(d):
    old = d.get("old") or ""; new = d.get("new")
    if not old or new is None: raise ValueError("Escribe el texto a buscar y el reemplazo")
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    count = 0; marks = []
    _van = 0
    for i in idx:
        page = doc[i]
        for r in page.search_for(old):
            page.add_redact_annot(r); marks.append((i, r)); count += 1
        _van += 1
        if d.get("_prog"): d["_prog"](_van * 90 // max(1, len(idx)))
    for i in idx: doc[i].apply_redactions()
    for i, r in marks:
        fs = max(6, (r.y1 - r.y0) * 0.82)
        doc[i].insert_text((r.x0, r.y0 + fs), new, fontsize=fs, fontname="helv", color=(0, 0, 0))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count, "replaced": count}


def _fontname(span_font):
    """Mapea la fuente original a la familia base-14 mas parecida."""
    low = (span_font or "").lower()
    bold = any(k in low for k in ("bold", "black", "heavy", "semibold"))
    ital = ("italic" in low) or ("oblique" in low)
    if "courier" in low or "mono" in low:
        base, suf = "co", {"": "ur", "b": "bo", "i": "it", "bi": "bi"}
    elif "times" in low or "roman" in low or "georgia" in low or "serif" in low:
        base, suf = "ti", {"": "ro", "b": "bo", "i": "it", "bi": "bi"}
    else:
        base, suf = "he", {"": "lv", "b": "bo", "i": "it", "bi": "bi"}
    key = ("b" if bold else "") + ("i" if ital else "")
    return base + suf.get(key, suf[""])

def api_text_at(d):
    """Devuelve la linea de texto bajo el punto (fx, fy relativos 0..1)."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    if d.get("password") and doc.authenticate(d["password"]) <= 0:
        raise ValueError("La contraseña no abre este PDF: revísala en el campo de Acceso (pestaña Archivo)")
    page = doc[int(d.get("page", 0))]
    W, H = page.rect.width, page.rect.height
    pt = pymupdf.Point(float(d["fx"]) * W, float(d["fy"]) * H)
    best = None; best_area = None; near = None; near_dist = 1e18
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0: continue
        for line in block["lines"]:
            spans = line["spans"]
            if not spans: continue
            text = "".join(s["text"] for s in spans)
            if not text.strip(): continue
            r = pymupdf.Rect(line["bbox"])
            if r.contains(pt):
                if best is None or r.width * r.height < best_area:
                    best = (line, r, text); best_area = r.width * r.height
            elif pymupdf.Rect(r.x0 - 2, r.y0 - 4, r.x1 + 2, r.y1 + 4).contains(pt):
                dist = ((r.x0 + r.x1) / 2 - pt.x) ** 2 + ((r.y0 + r.y1) / 2 - pt.y) ** 2
                if dist < near_dist: near = (line, r, text); near_dist = dist
    pick = best or near
    if not pick: return {"found": False, "page_w": W, "page_h": H}
    line, r, text = pick
    spans = line["spans"]
    dom = max(spans, key=lambda s: len(s["text"]))
    o = spans[0]["origin"]; col = dom["color"]
    return {"found": True, "text": text, "bbox": [r.x0, r.y0, r.x1, r.y1],
            "origin": [o[0], o[1]], "size": dom["size"], "font": dom["font"],
            "color": [(col >> 16 & 255) / 255, (col >> 8 & 255) / 255, (col & 255) / 255],
            "page_w": W, "page_h": H}

def api_edit_line(d):
    """Reemplaza UNA linea: borra la original (sin tocar bordes ni imagenes) y escribe la nueva en su sitio."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    if d.get("password") and doc.authenticate(d["password"]) <= 0:
        raise ValueError("La contraseña no abre este PDF: revísala en el campo de Acceso (pestaña Archivo)")
    page = doc[int(d.get("page", 0))]
    b = [float(v) for v in d["bbox"]]
    page.add_redact_annot(pymupdf.Rect(b[0] - 1, b[1] - 0.5, b[2] + 1, b[3] + 0.5))
    try:
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    except Exception:
        page.apply_redactions()
    new = d.get("text") or ""
    if new.strip():
        col = d.get("color") or [0, 0, 0]
        page.insert_text((float(d["origin"][0]), float(d["origin"][1])), new,
                         fontsize=float(d.get("size") or 11),
                         fontname=_fontname(d.get("font")),
                         color=(float(col[0]), float(col[1]), float(col[2])))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_make_cert(d):
    """Genera un certificado personal autofirmado (.pfx) para firmar PDFs."""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import pkcs12
    name = d.get("name") or "Usuario Aven PDF"
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name),
                         x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Aven PDF")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=1825))
            .add_extension(x509.KeyUsage(True, False, False, False, False, False, False, False, False), True)
            .sign(key, hashes.SHA256()))
    pfx = pkcs12.serialize_key_and_certificates(
        b"AvenPDF", key, cert, None,
        serialization.BestAvailableEncryption(d["password"].encode()))
    return {"file": b64e(pfx), "name": "mi_certificado_avenpdf.pfx"}

def api_sign(d):
    """Firma digital real (PAdES básica) con un certificado .pfx del usuario."""
    from cryptography.hazmat.primitives.serialization import pkcs12
    from endesive.pdf import cms
    try:
        key, cert, others = pkcs12.load_key_and_certificates(b64d(d["pfx"]), d["password"].encode())
    except Exception: raise ValueError("No se pudo abrir el certificado: contraseña incorrecta o archivo .pfx no válido")
    datau = P(d)
    dct = {"sigflags": 3, "contact": "", "location": "", "reason": d.get("reason") or "Firmado con Aven PDF",
           "signingdate": datetime.datetime.now(datetime.timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")}
    signed = cms.sign(datau, dct, key, cert, others or [], "sha256")
    out = datau + signed
    r = PdfReader(io.BytesIO(out))
    return {"pdf": b64e(out), "pages": len(r.pages), "fields": list((r.get_fields() or {}).keys())}

def api_insert_pdf(d):
    """Inserta todas las páginas de otro PDF justo después de la página 'at' (0-based)."""
    main = PdfReader(io.BytesIO(P(d)))
    other = PdfReader(io.BytesIO(b64d(d["other"])))
    at = int(d.get("at", 0))
    w = PdfWriter()
    if at < 0:
        for q in other.pages: w.add_page(q)
    for i, p in enumerate(main.pages):
        w.add_page(p)
        if i == at:
            for q in other.pages: w.add_page(q)
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages), "inserted": len(other.pages)}

def api_reorder(d):
    """Reordena las páginas según la lista de índices recibida (arrastrar miniaturas)."""
    r = PdfReader(io.BytesIO(P(d)))
    order = [int(x) for x in d["order"]]
    if sorted(order) != list(range(len(r.pages))):
        raise ValueError("Orden inválido")
    w = PdfWriter()
    for i in order: w.add_page(r.pages[i])
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}


def api_extract_images(d):
    """Extrae las imagenes INCRUSTADAS del PDF (no renderiza paginas)."""
    doc = pymupdf.open(stream=P(d), filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password", "")) <= 0:
        raise ValueError("El PDF tiene contraseña: escríbela en el campo de Acceso (pestaña Archivo) y vuelve a intentarlo.")
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    buf = io.BytesIO(); z = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    seen = set(); n = 0; _van = 0
    for i in idx:
        for img in doc[i].get_images(full=True):
            xref = img[0]
            if xref in seen: continue
            seen.add(xref)
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.n > 3: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
                data = pix.tobytes("png")
            except Exception:
                continue
            n += 1
            z.writestr(f"pagina{i+1}_imagen{n}.png", data)
        _van += 1
        if d.get("_prog"): d["_prog"](_van * 100 // max(1, len(idx)))
    z.close()
    return {"zip": b64e(buf.getvalue()), "count": n, "pages": len(idx)}

def api_to_scanned(d):
    """Convierte el PDF en otro que PARECE salido de un escáner o una
    fotocopiadora real: la hoja entra levemente girada sobre el cristal,
    con su borde y su sombra, luz desigual con viñeta, textura y desgaste
    del papel, motas de polvo y el grano del sensor. El texto NO se
    desenfoca: se sigue leyendo perfecto."""
    import random
    import numpy as np
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
    doc = _open_tol(d)
    mode = d.get("mode", "color")
    out = pymupdf.open()
    rnd = random.Random(20261017)
    for _pi, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2.35, 2.35))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        w, h = img.size
        rng = np.random.default_rng(rnd.randrange(1 << 30))
        a = np.asarray(img).astype(np.float32)
        gx = np.linspace(rnd.uniform(0.96, 0.99), 1.0, w, dtype=np.float32)[None, :, None]
        gy = np.linspace(1.0, rnd.uniform(0.97, 0.995), h, dtype=np.float32)[:, None, None]
        yy, xx = np.mgrid[0:h, 0:w]
        vig = 1 - 0.028 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        a = a * gx * gy * vig[..., None].astype(np.float32)
        a = np.clip(a * np.array([rnd.uniform(1.005, 1.02), 1.0, rnd.uniform(0.972, 0.99)], dtype=np.float32), 0, 255)
        mot = rng.normal(0, 1, (h // 46 + 2, w // 46 + 2)).astype(np.float32)
        mot = (mot - mot.min()) / (np.ptp(mot) + 1e-6)
        mot = np.asarray(Image.fromarray((mot * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0
        a = np.clip(a * (0.965 + 0.07 * mot[..., None]), 0, 255)
        a = np.clip(a + rng.normal(0, 3.1, a.shape[:2])[..., None].astype(np.float32), 0, 255)
        img = Image.fromarray(a.astype(np.uint8))
        dr = ImageDraw.Draw(img, "RGBA")
        for _ in range(rnd.randrange(6, 26)):
            x0, y0 = rnd.uniform(0, w), rnd.uniform(0, h)
            r0 = rnd.uniform(0.6, 2.2)
            dr.ellipse((x0 - r0, y0 - r0, x0 + r0, y0 + r0), fill=(60, 55, 45, rnd.randrange(28, 70)))
        img = img.filter(ImageFilter.GaussianBlur(0.35))
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=68, threshold=2))
        if mode == "bw":
            img = img.convert("L")
            img = ImageEnhance.Contrast(img).enhance(1.22)
            img = ImageEnhance.Brightness(img).enhance(1.03)
            img = img.convert("RGB")
        else:
            img = ImageEnhance.Color(img).enhance(0.86)
            img = ImageEnhance.Contrast(img).enhance(1.06)
        mx, my = int(w * 0.035), int(h * 0.03)
        bed = Image.new("RGB", (w + 2 * mx, h + 2 * my), (214, 214, 210))
        ba = np.asarray(bed).astype(np.float32)
        ba = np.clip(ba + rng.normal(0, 2.0, ba.shape[:2])[..., None].astype(np.float32), 0, 255)
        bed = Image.fromarray(ba.astype(np.uint8))
        sh = Image.new("RGB", bed.size, (214, 214, 210))
        shd = ImageDraw.Draw(sh)
        ox, oy = rnd.choice((-1, 1)) * int(w * 0.008), int(h * 0.01)
        shd.rectangle((mx + ox, my + oy, mx + w + ox, my + h + oy), fill=(118, 118, 114))
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        bed = Image.blend(bed, sh, 0.35)
        ang = rnd.uniform(0.3, 0.9) * rnd.choice((-1, 1))
        sheet = img.rotate(ang, resample=Image.BICUBIC, expand=False, fillcolor=(250, 250, 247))
        bed.paste(sheet, (mx, my))
        bd = ImageDraw.Draw(bed)
        bd.rectangle((mx, my, mx + w - 1, my + h - 1), outline=(168, 166, 160), width=2)
        buf = io.BytesIO(); bed.save(buf, "JPEG", quality=80)
        npg = out.new_page(width=page.rect.width * (w + 2 * mx) / w,
                           height=page.rect.height * (h + 2 * my) / h)
        npg.insert_image(npg.rect, stream=buf.getvalue())
        if d.get("_prog"): d["_prog"]((_pi + 1) * 100 // doc.page_count)
    return {"pdf": b64e(out.tobytes(garbage=3, deflate=True)), "pages": out.page_count}

def _skew_angle(imgL):
    """Ángulo de inclinación (grados) de una página en gris: proyección de
    filas con criterio de energía (suma de cuadrados), que da un pico
    mucho más nítido que la varianza; dos pasadas (gruesa y fina)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(imgL, dtype=np.uint8)
    h, w = a.shape
    a = a[int(h * 0.04):int(h * 0.96), int(w * 0.03):int(w * 0.97)]
    if (a < 160).sum() < 80: return 0.0
    base = Image.fromarray(a)
    def score(ang):
        r = base.rotate(ang, resample=Image.BILINEAR, fillcolor=255)
        rows = (np.asarray(r, dtype=np.float32) < 160).sum(axis=1)
        return float((rows * rows).sum())
    best, bestv = 0.0, -1.0
    k = -6.0
    while k <= 6.01:
        v = score(k)
        if v > bestv: bestv, best = v, k
        k += 0.5
    k = best - 0.6
    while k <= best + 0.601:
        kk = round(k, 2)
        v = score(kk)
        if v > bestv: bestv, best = v, kk
        k += 0.1
    return best

def api_deskew(d):
    """Endereza paginas chuecas: detecta el angulo y lo corrige (salida en imagen)."""
    from PIL import Image
    doc = _open_tol(d)
    idx = set(parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count)))
    out = pymupdf.open(); fixed = 0
    for i, page in enumerate(doc):
        ang = 0.0
        if i in idx:
            pix0 = page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2))
            img0 = Image.frombytes("RGB", (pix0.width, pix0.height), pix0.samples)
            small = img0.convert("L"); small.thumbnail((850, 1200))
            ang = _skew_angle(small)
        if d.get("_prog"): d["_prog"]((i + 1) * 100 // doc.page_count)
        if i not in idx or abs(ang) < 0.12:
            # Página no tocada o ya derecha: se copia TAL CUAL (conserva su
            # texto buscable); antes TODO el documento salía convertido en
            # imagen aunque solo se corrigieran unas páginas.
            out.insert_pdf(doc, from_page=i, to_page=i)
            continue
        img = img0.rotate(ang, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
        fixed += 1
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=80)
        npg = out.new_page(width=page.rect.width, height=page.rect.height)
        npg.insert_image(npg.rect, stream=buf.getvalue())
    return {"pdf": b64e(out.tobytes(garbage=3, deflate=True)), "fixed": fixed, "pages": out.page_count}

# ===== Trabajos largos con progreso (1.8) =====
# Las operaciones que pueden tardar (comprimir, OCR, enderezar...) corren en
# un hilo y van reportando su avance; la interfaz pregunta cada medio segundo
# y muestra el porcentaje y el tiempo estimado que falta. Las operaciones
# reportan llamando a d["_prog"](porcentaje) en su bucle de paginas.
JOBS = {}
JOBS_LOCK = threading.Lock()

def _job_cb(jid):
    def cb(pct):
        with JOBS_LOCK:
            j = JOBS.get(jid)
            if j is None: return
            if j.get("cancel"):
                raise RuntimeError("Cancelado por el usuario")
            j["pct"] = max(0, min(99, int(pct))); j["known"] = True
    return cb

DL_STAGE = {}
DL_LOCK = threading.Lock()

def api_stage_download(d):
    data = b64d(d.get("data") or "")
    if not data: raise ValueError("Nada para descargar")
    tok = uuid.uuid4().hex[:16]
    with DL_LOCK:
        DL_STAGE[tok] = (data, d.get("name") or "archivo.pdf",
                         d.get("mime") or "application/pdf", time.time())
        for _k in [k for k, v in DL_STAGE.items() if time.time() - v[3] > 900]:
            DL_STAGE.pop(_k, None)
    return {"url": "/dl/" + tok}

_T0 = time.time()

def api_winmode(d):
    import sys as _s
    if "--ventana" not in _s.argv:
        return {"mode": "navegador"}
    try:
        import os as _o
        okf = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "aven_ventana.ok")
        if _o.path.exists(okf) and _o.path.getmtime(okf) > _T0 - 120:
            return {"mode": "nativa"}
    except Exception:
        pass
    return {"mode": "respaldo Edge"}

def api_job_start(d):
    op = d.get("op") or ""
    fn = APIS.get(op)
    if fn is None or op.startswith("/api/job") or op == "/api/fetch_doc":
        raise ValueError("Operación no válida para una tarea larga")
    args = dict(d.get("args") or {})
    if args.get("doc_id"):
        with DOCS_LOCK:
            _data = DOCS.get(args["doc_id"])
            if _data is not None: DOCS.move_to_end(args["doc_id"])
        if _data is None:
            raise ValueError("El documento ya no está en la memoria del programa (se abrieron otros después). Vuelve a abrir el PDF.")
        args["_raw"] = _data
    jid = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        for _k in [k for k, v in JOBS.items() if v.get("done") and time.time() - v["t0"] > 600]:
            JOBS.pop(_k, None)
        JOBS[jid] = {"pct": 0, "done": False, "cancel": False,
                     "t0": time.time(), "result": None, "error": None}
    def _run():
        args["_prog"] = _job_cb(jid)
        try:
            out = fn(args)
            if isinstance(out, dict) and isinstance(out.get("pdf"), str):
                try: out["doc_id"] = store_doc(b64d(out["pdf"]))
                except Exception: pass
            with JOBS_LOCK: JOBS[jid].update(done=True, result=out, pct=100)
        except Exception as e:
            with JOBS_LOCK: JOBS[jid].update(done=True, error=str(e))
    threading.Thread(target=_run, daemon=True).start()
    return {"job": jid}

def api_job_status(d):
    with JOBS_LOCK:
        j = JOBS.get(d.get("job") or "")
        if j is None:
            raise ValueError("Esa tarea ya no existe (el programa se reinició o la tarea expiró)")
        el = time.time() - j["t0"]; pct = j["pct"]
        out = {"done": j["done"], "pct": pct, "elapsed": round(el), "known": bool(j.get("known")),
               "eta": (round(el * (100 - pct) / pct) if (not j["done"] and pct > 0) else None)}
        if j["done"]:
            if j.get("error"): out["error"] = _friendly_err(Exception(j["error"]))
            else: out["result"] = j["result"]
            JOBS.pop(d.get("job"), None)
    return out

def api_job_cancel(d):
    with JOBS_LOCK:
        j = JOBS.get(d.get("job") or "")
        if j is not None: j["cancel"] = True
    return {"ok": True}

def _friendly_err(e):
    """Traduce los errores crudos de las librerías a español claro."""
    m = str(e)
    low = m.lower()
    if ("decrypt" in low or "encrypted" in low or "invalid password" in low
            or "password" in low and "contraseña" not in m):
        return ("El PDF está protegido con contraseña: escríbela en el campo "
                "de Acceso (pestaña Archivo) y vuelve a intentarlo.")
    if "document closed" in low:
        return "El documento se cerró inesperadamente; vuelve a abrir el PDF."
    return m

APIS = {"/api/open": api_open, "/api/info": api_info, "/api/render": api_render, "/api/merge": api_merge,
        "/api/insert_pdf": api_insert_pdf, "/api/reorder": api_reorder,
        "/api/to_word": api_to_word, "/api/to_excel": api_to_excel,
        "/api/ocr_text": api_ocr_text, "/api/ocr_pdf": api_ocr_pdf,
        "/api/replace_text": api_replace_text, "/api/make_cert": api_make_cert,
        "/api/text_at": api_text_at, "/api/edit_line": api_edit_line,
        "/api/sign": api_sign,
        "/api/extract": api_extract, "/api/split_each": api_split_each, "/api/split": api_split,
        "/api/rotate": api_rotate, "/api/delete_pages": api_delete_pages,
        "/api/watermark": api_watermark, "/api/watermark_image": api_watermark_image,
        "/api/add_text": api_add_text,
        "/api/stamp": api_stamp, "/api/encrypt": api_encrypt,
        "/api/decrypt": api_decrypt, "/api/compress": api_compress,
        "/api/to_images": api_to_images, "/api/to_text": api_to_text,
        "/api/images_to_pdf": api_images_to_pdf, "/api/text_to_pdf": api_text_to_pdf,
        "/api/form_fields": api_form_fields, "/api/fill_form": api_fill_form, "/api/extract_images": api_extract_images,
        "/api/to_scanned": api_to_scanned, "/api/deskew": api_deskew,
        "/api/fetch_doc": api_fetch_doc,
        "/api/stage_download": api_stage_download, "/api/winmode": api_winmode,
        "/api/job_start": api_job_start, "/api/job_status": api_job_status,
        "/api/job_cancel": api_job_cancel}

from aven_ui import UI

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith("/dl/"):
            from urllib.parse import quote as _q
            tok = self.path[4:].split("?")[0]
            with DL_LOCK: ent = DL_STAGE.pop(tok, None)
            if ent is None:
                self.send_response(404); self.end_headers(); return
            data, name, mime, _t = ent
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + _q(name))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data)
            return
        if self.path in ("/", "/index.html"):
            body = UI.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        fn = APIS.get(self.path)
        if not fn:
            self.send_response(404); self.end_headers(); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
            if d.get("doc_id"):
                with DOCS_LOCK:
                    _data = DOCS.get(d["doc_id"])
                    if _data is not None: DOCS.move_to_end(d["doc_id"])
                if _data is None:
                    raise ValueError("El documento ya no está en la memoria del programa (se abrieron otros después). Vuelve a abrir el PDF.")
                d["_raw"] = _data
            out = fn(d); code = 200
            if self.path != "/api/fetch_doc" and isinstance(out, dict) and isinstance(out.get("pdf"), str):
                try: out["doc_id"] = store_doc(b64d(out["pdf"]))
                except Exception: pass
            if d.get("light") and isinstance(out, dict) and out.get("doc_id") and isinstance(out.get("pdf"), str):
                out = dict(out); out["pdf"] = None  # la interfaz lo adopta por doc_id
        except Exception as e:
            out = {"error": _friendly_err(e)}; code = 400
        body = json.dumps(out).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

if __name__ == "__main__":
    import sys, threading, time
    if "--ventana" in sys.argv:
        PORT = 8890  # la edición instalada usa su propio puerto
    def _serve():
        ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
    print(f"Aven PDF escuchando en http://127.0.0.1:{PORT}  (Ctrl+C para cerrar)")
    if "--ventana" in sys.argv:
        import os as _os, traceback as _tb, subprocess as _sp
        _dir = _os.path.dirname(_os.path.abspath(__file__))
        def _log(msg):
            try:
                with open(_os.path.join(_dir, "aven_ventana.log"), "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            except Exception:
                pass
        _log("=== inicio en modo ventana ===")
        if sys.platform == "win32":
            try:
                import ctypes as _ct
                _mutex = _ct.windll.kernel32.CreateMutexW(None, False, "AvenPDFVentana")
            except Exception:
                pass
        threading.Thread(target=_serve, daemon=True).start()
        time.sleep(1.2)

        def _respaldo_edge():
            # Respaldo: Edge en modo aplicación (ventana sin barra de direcciones)
            _edge = None
            for _cand in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                          r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
                if _os.path.exists(_cand):
                    _edge = _cand
                    break
            if _edge:
                try:
                    _log("respaldo: Edge en modo app -> " + _edge)
                    _sp.Popen([_edge, f"--app=http://127.0.0.1:{PORT}", "--window-size=1440,950"])
                    while True: time.sleep(3600)
                except Exception:
                    _log("FALLO respaldo Edge app:\n" + _tb.format_exc())
            import webbrowser
            webbrowser.open(f"http://127.0.0.1:{PORT}")
            try:
                while True: time.sleep(3600)
            except KeyboardInterrupt:
                pass

        # La ventana corre en un PROCESO HIJO y debe PROBAR que abrió:
        # escribe una señal cuando la página carga dentro de ella. Si el
        # hijo muere antes de la señal, o pasan 25 s sin señal (estrellón
        # nativo que deja el proceso zombi, como pasaba en algunas PC),
        # el servidor sobrevive y entra el respaldo en vez de no abrir nada.
        _marca = _os.path.join(_dir, "aven_ventana.ok")
        _bien = False
        _hijo = None
        for _intento in (1, 2):
            try: _os.remove(_marca)
            except Exception: pass
            _hijo = _sp.Popen([sys.executable, _os.path.abspath(__file__), "--solo-ventana"])
            _t0 = time.time()
            while time.time() - _t0 < 10:
                if _os.path.exists(_marca):
                    _bien = True
                    break
                if _hijo.poll() is not None:
                    break
                time.sleep(0.3)
            if _bien:
                break
            _log("ventana propia: intento %d sin senal; %s" % (_intento,
                 "reintentando" if _intento == 1 else "va el respaldo"))
            try: _hijo.kill()
            except Exception: pass
            try: _hijo.wait(timeout=3)
            except Exception: pass
            time.sleep(0.6)
        if not _bien:
            _respaldo_edge()
        else:
            _log("ventana propia en marcha")
            try:
                _hijo.wait()
            except KeyboardInterrupt:
                pass
            _log("ventana cerrada; fin del programa")
    elif "--solo-ventana" in sys.argv:
        # Proceso hijo: solo abre la ventana nativa contra el servidor del padre.
        import os as _os, traceback as _tb
        _dir = _os.path.dirname(_os.path.abspath(__file__))
        def _log(msg):
            try:
                with open(_os.path.join(_dir, "aven_ventana.log"), "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            except Exception:
                pass
        try:
            import faulthandler as _fh
            _fh.enable(file=open(_os.path.join(_dir, "aven_ventana.log"), "a", encoding="utf-8"), all_threads=True)
        except Exception:
            pass
        try:
            _log("importando pywebview...")
            import webview
            _log("pywebview importado; creando la ventana")
            _win = webview.create_window("Aven PDF", "http://127.0.0.1:8890",
                                  width=1440, height=950, min_size=(1000, 700),
                                  shadow=False)
            def _senal():
                # La página cargó dentro de la ventana: avisar al padre.
                try:
                    with open(_os.path.join(_dir, "aven_ventana.ok"), "w", encoding="utf-8") as f:
                        f.write("ok")
                except Exception:
                    pass
            try: _win.events.loaded += _senal
            except Exception: pass
            _datos = _os.path.join(_dir, "webview-data")
            try: _os.makedirs(_datos, exist_ok=True)
            except Exception: pass
            try:
                webview.start(gui="edgechromium", storage_path=_datos)
            except TypeError:
                try:
                    webview.start(gui="edgechromium")
                except TypeError:
                    webview.start()
            _log("ventana cerrada normalmente")
        except Exception:
            _log("FALLO ventana propia:\n" + _tb.format_exc())
            raise
    else:
        _serve()
