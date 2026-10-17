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
        else:
            try: rng = [int(part)]
            except ValueError: raise ValueError("Páginas no válidas: usa números y rangos como 1-3,5")
        for n in rng:
            if 1 <= n <= total and (n - 1) not in out:
                out.append(n - 1)
    return out

def api_info(d):
    data = b64d(d["pdf"])
    try: doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception: raise ValueError("El archivo no es un PDF válido o está dañado")
    if doc.is_encrypted and not doc.authenticate(d.get("password") or ""):
        raise ValueError("El PDF está protegido con contraseña: escríbela en el campo de Acceso (pestaña Archivo) y vuelve a abrirlo")
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
import threading, uuid
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
RENDER_CACHE_MAX = 240

def api_open(d):
    """Registra el PDF en el almacén y devuelve su info + doc_id."""
    data = b64d(d["pdf"])
    info = api_info(d)
    info["doc_id"] = store_doc(data)
    return info

def api_render(d):
    _ckey = None
    if d.get("doc_id"):
        _ckey = (d["doc_id"], int(d.get("page", 0)),
                 round(float(d.get("zoom", 1.4)), 3), d.get("password") or "")
        if _ckey in RENDER_CACHE:
            RENDER_CACHE.move_to_end(_ckey)
            return dict(RENDER_CACHE[_ckey])
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if doc.is_encrypted and not doc.authenticate(d.get("password") or ""):
        raise ValueError("El PDF está protegido: escribe su contraseña en Acceso (pestaña Archivo)")
    page = doc[int(d.get("page", 0))]
    zoom = float(d.get("zoom", 1.4))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    out = {"png": b64e(pix.tobytes("png")), "pages": doc.page_count,
           "w": pix.width, "h": pix.height}
    if _ckey:
        RENDER_CACHE[_ckey] = out
        while len(RENDER_CACHE) > RENDER_CACHE_MAX:
            RENDER_CACHE.popitem(last=False)
    return out

def api_merge(d):
    w = PdfWriter()
    for item in d["pdfs"]:
        r = PdfReader(io.BytesIO(b64d(item)))
        for p in r.pages: w.add_page(p)
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_extract(d):
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    idx = parse_pages(d.get("pages", ""), len(r.pages))
    if not idx: raise ValueError("Indica páginas, p. ej. 1-3,5")
    w = PdfWriter()
    for i in idx: w.add_page(r.pages[i])
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_split_each(d):
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for i, p in enumerate(r.pages, 1):
            w = PdfWriter(); w.add_page(p)
            b = io.BytesIO(); w.write(b)
            z.writestr(f"pagina_{i:03d}.pdf", b.getvalue())
    return {"zip": b64e(zbuf.getvalue()), "pages": len(r.pages)}

def api_split(d):
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
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
        for nm, idx in parts:
            w = PdfWriter()
            for i in idx: w.add_page(r.pages[i])
            b = io.BytesIO(); w.write(b)
            z.writestr(nm, b.getvalue())
    return {"zip": b64e(zbuf.getvalue()), "parts": len(parts)}

def api_rotate(d):
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    idx = parse_pages(d.get("pages", ""), len(r.pages)) or list(range(len(r.pages)))
    deg = int(d.get("degrees", 90))
    w = PdfWriter()
    for i, p in enumerate(r.pages):
        if i in idx: p.rotate(deg)
        w.add_page(p)
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_delete_pages(d):
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    drop = set(parse_pages(d.get("pages", ""), len(r.pages)))
    if not drop: raise ValueError("Indica qué páginas borrar")
    if len(drop) >= len(r.pages): raise ValueError("No puedes borrar todas las páginas")
    w = PdfWriter()
    for i, p in enumerate(r.pages):
        if i not in drop: w.add_page(p)
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_watermark(d):
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    text = d.get("text") or "Aven PDF"
    for page in doc:
        r = page.rect
        fs = max(28, r.width / max(6, len(text)) * 1.1)
        op = float(d.get("opacity", 0.25))
        pt = pymupdf.Point(r.width * 0.08, r.height * 0.55)
        page.insert_text(pt, text,
                         fontsize=fs, fontname="helv", color=(0.55, 0.6, 0.7),
                         fill_opacity=op, stroke_opacity=op,
                         morph=(pt, pymupdf.Matrix(35)))
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_add_text(d):
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
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
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
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
    for page in doc:
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
    return {"pdf": b64e(doc.tobytes(garbage=3, deflate=True)), "pages": doc.page_count}

def api_stamp(d):
    """Sello de firma tipo np_signature_stamp: nombre + fecha, marco fino."""
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
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
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    w = PdfWriter()
    for p in r.pages: w.add_page(p)
    w.encrypt(d["password"], algorithm="AES-256")
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_decrypt(d):
    try:
        r = PdfReader(io.BytesIO(b64d(d["pdf"])), password=d.get("password") or None)
        w = PdfWriter()
        for p in r.pages: w.add_page(p)
    except Exception: raise ValueError("Contraseña incorrecta: no se pudo abrir el PDF")
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}

def api_compress(d):
    data = b64d(d["pdf"])
    doc = pymupdf.open(stream=data, filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password") or "") <= 0:
        raise ValueError("El PDF tiene contraseña: ábrelo primero con su contraseña.")
    dpi, calidad = {"pantalla": (150, 58), "media": (200, 74),
                    "alta": (300, 88)}.get(d.get("level"), (200, 74))
    # Ancho en pixeles que necesita cada imagen según el tamaño al que se
    # muestra en su página (una foto gigante mostrada chica sobra en pixeles).
    need = {}
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            for r in page.get_image_rects(xref):
                px = r.width / 72.0 * dpi
                if px > need.get(xref, 0): need[xref] = px
    from PIL import Image
    hechas = 0
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
            for page in doc:
                if any(i2[0] == xref for i2 in page.get_images(full=True)):
                    page.replace_image(xref, stream=nuevo)
            hechas += 1
            del pix, im, nuevo
            if hechas % 20 == 0:
                import gc; gc.collect()
        except Exception:
            continue
    out = doc.tobytes(garbage=4, deflate=True)
    return {"pdf": b64e(out), "pages": doc.page_count, "images_done": hechas,
            "before_kb": round(len(data) / 1024, 1), "after_kb": round(len(out) / 1024, 1)}

def api_to_images(d):
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    zoom = float(d.get("zoom", 2.0))
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            z.writestr(f"pagina_{i:03d}.png", pix.tobytes("png"))
    return {"zip": b64e(zbuf.getvalue()), "pages": doc.page_count}

def api_to_text(d):
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    parts = []
    for i, page in enumerate(doc, 1):
        parts.append(f"===== Página {i} =====\n" + page.get_text())
    return {"text": "\n\n".join(parts), "pages": doc.page_count}

def api_images_to_pdf(d):
    doc = pymupdf.open()
    for item in d["images"]:
        img = b64d(item)
        pix = pymupdf.Pixmap(img)
        page = doc.new_page(width=pix.width, height=pix.height)
        page.insert_image(pymupdf.Rect(0, 0, pix.width, pix.height), stream=img)
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
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    f = r.get_fields() or {}
    return {"fields": [{"name": k, "type": str(v.get("/FT", "")), "value": str(v.get("/V", "") or "")}
                        for k, v in f.items()]}

def api_fill_form(d):
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
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
        open(src, "wb").write(b64d(d["pdf"]))
        cv = Converter(src)
        try: cv.convert(dst, start=0, end=None, multi_processing=False)
        finally: cv.close()
        data = open(dst, "rb").read()
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    return {"file": b64e(data), "name": "convertido.docx", "pages": doc.page_count}

def api_to_excel(d):
    """PDF -> Excel (.xlsx): una hoja por página con las tablas detectadas."""
    import pdfplumber
    from openpyxl import Workbook
    wb = Workbook(); wb.remove(wb.active)
    total_tables = 0
    with pdfplumber.open(io.BytesIO(b64d(d["pdf"]))) as pdf:
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
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    parts = []
    for i in idx:
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(3, 3))
        lines = [t for (_b, t, _c) in _ocr_page(pix)]
        parts.append(f"===== Página {i+1} (OCR) =====\n" + "\n".join(lines))
    return {"text": "\n\n".join(parts), "pages": len(idx)}

def api_ocr_pdf(d):
    """Crea un PDF buscable: imagen de la página + capa de texto invisible OCR."""
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    out = pymupdf.open()
    zoom = 3
    for page in doc:
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
    return {"pdf": b64e(out.tobytes(garbage=3, deflate=True)), "pages": out.page_count}

def api_replace_text(d):
    old = d.get("old") or ""; new = d.get("new")
    if not old or new is None: raise ValueError("Escribe el texto a buscar y el reemplazo")
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    count = 0; marks = []
    for i in idx:
        page = doc[i]
        for r in page.search_for(old):
            page.add_redact_annot(r); marks.append((i, r)); count += 1
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
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if d.get("password"): doc.authenticate(d["password"])
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
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if d.get("password"): doc.authenticate(d["password"])
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
    datau = b64d(d["pdf"])
    dct = {"sigflags": 3, "contact": "", "location": "", "reason": d.get("reason") or "Firmado con Aven PDF",
           "signingdate": datetime.datetime.now(datetime.timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")}
    signed = cms.sign(datau, dct, key, cert, others or [], "sha256")
    out = datau + signed
    r = PdfReader(io.BytesIO(out))
    return {"pdf": b64e(out), "pages": len(r.pages), "fields": list((r.get_fields() or {}).keys())}

def api_insert_pdf(d):
    """Inserta todas las páginas de otro PDF justo después de la página 'at' (0-based)."""
    main = PdfReader(io.BytesIO(b64d(d["pdf"])))
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
    r = PdfReader(io.BytesIO(b64d(d["pdf"])))
    order = [int(x) for x in d["order"]]
    if sorted(order) != list(range(len(r.pages))):
        raise ValueError("Orden inválido")
    w = PdfWriter()
    for i in order: w.add_page(r.pages[i])
    buf = io.BytesIO(); w.write(buf)
    return {"pdf": b64e(buf.getvalue()), "pages": len(w.pages)}


def api_extract_images(d):
    """Extrae las imagenes INCRUSTADAS del PDF (no renderiza paginas)."""
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password", "")) <= 0:
        raise ValueError("El PDF tiene contraseña: escríbela en el campo de Acceso (pestaña Archivo) y vuelve a intentarlo.")
    idx = parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count))
    buf = io.BytesIO(); z = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    seen = set(); n = 0
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
    z.close()
    return {"zip": b64e(buf.getvalue()), "count": n, "pages": len(idx)}

def api_to_scanned(d):
    """Convierte el PDF en otro que PARECE escaneado (lookscanned)."""
    import random
    from PIL import Image, ImageEnhance, ImageFilter
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password", "")) <= 0:
        raise ValueError("El PDF tiene contraseña: escríbela en el campo de Acceso (pestaña Archivo) y vuelve a intentarlo.")
    mode = d.get("mode", "color")
    out = pymupdf.open()
    rnd = random.Random(20261017)
    for page in doc:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img = img.rotate(rnd.uniform(-0.5, 0.5), resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
        img = img.filter(ImageFilter.GaussianBlur(0.5))
        if mode == "bw":
            img = img.convert("L")
            img = ImageEnhance.Contrast(img).enhance(1.25)
            img = ImageEnhance.Brightness(img).enhance(1.04)
        else:
            img = ImageEnhance.Color(img).enhance(0.8)
            img = ImageEnhance.Contrast(img).enhance(1.05)
            img = ImageEnhance.Brightness(img).enhance(1.02)
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=72)
        npg = out.new_page(width=page.rect.width, height=page.rect.height)
        npg.insert_image(npg.rect, stream=buf.getvalue())
    return {"pdf": b64e(out.tobytes(garbage=3, deflate=True)), "pages": out.page_count}

def _skew_angle(imgL):
    """Angulo de inclinacion (grados) de una pagina en gris, por proyeccion de filas."""
    import numpy as np
    from PIL import Image
    a = np.asarray(imgL, dtype=np.uint8)
    if (a < 128).sum() < 60: return 0.0
    best, bestv = 0.0, -1.0
    for k in range(-20, 21):
        ang = k * 0.25
        r = Image.fromarray(a).rotate(ang, resample=Image.BILINEAR, fillcolor=255)
        v = float((np.asarray(r, dtype=np.float32) < 128).sum(axis=1).var())
        if v > bestv: bestv, best = v, ang
    return best

def api_deskew(d):
    """Endereza paginas chuecas: detecta el angulo y lo corrige (salida en imagen)."""
    from PIL import Image
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if doc.needs_pass and doc.authenticate(d.get("password", "")) <= 0:
        raise ValueError("El PDF tiene contraseña: escríbela en el campo de Acceso (pestaña Archivo) y vuelve a intentarlo.")
    idx = set(parse_pages(d.get("pages", ""), doc.page_count) or list(range(doc.page_count)))
    out = pymupdf.open(); fixed = 0
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if i in idx:
            small = img.convert("L"); small.thumbnail((700, 990))
            ang = _skew_angle(small)
            if abs(ang) >= 0.3:
                img = img.rotate(ang, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
                fixed += 1
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=80)
        npg = out.new_page(width=page.rect.width, height=page.rect.height)
        npg.insert_image(npg.rect, stream=buf.getvalue())
    return {"pdf": b64e(out.tobytes(garbage=3, deflate=True)), "fixed": fixed, "pages": out.page_count}

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
        "/api/to_scanned": api_to_scanned, "/api/deskew": api_deskew}

from aven_ui import UI

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
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
                d["pdf"] = b64e(_data)
            out = fn(d); code = 200
            if isinstance(out, dict) and isinstance(out.get("pdf"), str):
                try: out["doc_id"] = store_doc(b64d(out["pdf"]))
                except Exception: pass
        except Exception as e:
            out = {"error": str(e)}; code = 400
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
        import os as _os, traceback as _tb
        _dir = _os.path.dirname(_os.path.abspath(__file__))
        def _log(msg):
            try:
                with open(_os.path.join(_dir, "aven_ventana.log"), "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            except Exception:
                pass
        _log("=== inicio en modo ventana ===")
        threading.Thread(target=_serve, daemon=True).start()
        time.sleep(1.2)
        try:
            _log("importando pywebview...")
            import webview
            _log("pywebview importado; creando la ventana")
            webview.create_window("Aven PDF", f"http://127.0.0.1:{PORT}",
                                  width=1440, height=950, min_size=(1000, 700))
            try:
                webview.start(gui="edgechromium")
            except TypeError:
                webview.start()
            _log("ventana cerrada normalmente")
        except Exception:
            _log("FALLO ventana propia:\n" + _tb.format_exc())
            # Respaldo 1: Edge en modo aplicación (ventana propia, sin barra de direcciones)
            _edge = None
            for _cand in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                          r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
                if _os.path.exists(_cand):
                    _edge = _cand
                    break
            if _edge:
                try:
                    import subprocess as _sp
                    _log("respaldo: Edge en modo app -> " + _edge)
                    _sp.Popen([_edge, f"--app=http://127.0.0.1:{PORT}", "--window-size=1440,950"])
                    while True: time.sleep(3600)
                except Exception:
                    _log("FALLO respaldo Edge app:\n" + _tb.format_exc())
            # Respaldo 2: navegador normal
            import webbrowser
            webbrowser.open(f"http://127.0.0.1:{PORT}")
            try:
                while True: time.sleep(3600)
            except KeyboardInterrupt:
                pass
    else:
        _serve()
