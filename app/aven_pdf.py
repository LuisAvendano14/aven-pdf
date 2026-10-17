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
            "page_sizes": [[round(p.rect.width), round(p.rect.height)] for p in doc][:50],
            "bookmarks": len(doc.get_toc()),
            "toc": [[lv, t, pg] for (lv, t, pg) in doc.get_toc()]}

def api_render(d):
    doc = pymupdf.open(stream=b64d(d["pdf"]), filetype="pdf")
    if doc.is_encrypted and not doc.authenticate(d.get("password") or ""):
        raise ValueError("El PDF está protegido: escribe su contraseña en Acceso (pestaña Archivo)")
    page = doc[int(d.get("page", 0))]
    zoom = float(d.get("zoom", 1.4))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return {"png": b64e(pix.tobytes("png")), "pages": doc.page_count,
            "w": pix.width, "h": pix.height}

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
    out = doc.tobytes(garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
    return {"pdf": b64e(out), "pages": doc.page_count,
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
        from rapidocr_onnxruntime import RapidOCR
        _OCR_ENGINE = RapidOCR()
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

APIS = {"/api/info": api_info, "/api/render": api_render, "/api/merge": api_merge,
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
        "/api/form_fields": api_form_fields, "/api/fill_form": api_fill_form}

UI = r"""
<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aven PDF</title>
<link rel="icon" id="favIco" href="data:,">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<style>
:root{--az:#1E40AF;--az2:#0F172A;--bg:#F1F5F9;--panel:#ffffff;--ink:#1E293B;--mut:#64748B;--line:#E2E8F0;--ok:#15803d;--err:#dc2626;--rib:#ffffff;--acc:#EA580C}
*{box-sizing:border-box} body{margin:0;font-family:Inter,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--ink);display:flex;flex-direction:column;height:100vh;overflow:hidden}
.topbar{display:flex;align-items:center;gap:14px;background:var(--az2);color:#fff;padding:8px 16px;border-bottom:3px solid var(--acc)}
.topbar .ver{background:var(--acc);color:#fff;font-size:12px;font-weight:700;border-radius:20px;padding:2px 10px;vertical-align:middle}
#pagebar{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:6px;background:#f4f6fb;border-bottom:1px solid var(--line);padding:7px 12px}
.pb{display:flex;gap:6px;align-items:center;flex-wrap:wrap;min-width:0}.pb.c{flex-wrap:nowrap}.pb.c{justify-self:center}.pb.r{justify-self:end}
.titem{cursor:grab;border-radius:6px;padding:3px 1px}.titem:active{cursor:grabbing}.titem.dragov{outline:2px dashed var(--acc);outline-offset:-2px}
#pagesBox{display:flex;flex-direction:column;align-items:center;gap:18px}
.cpage{background:#fff;box-shadow:0 4px 18px rgba(0,0,0,.4);max-width:100%}
.tabs button[data-t="inicio"]{background:var(--acc);color:#fff;font-weight:700}
#insDlg{position:fixed;inset:0;background:rgba(10,18,35,.45);display:none;align-items:center;justify-content:center;z-index:50}
#insDlg .box{background:#fff;border-radius:14px;padding:22px 26px;text-align:center;box-shadow:0 12px 40px rgba(0,0,0,.35);max-width:360px}
#insDlg button{display:block;width:100%;margin:8px 0;padding:11px;border-radius:9px;border:1px solid var(--line);background:#f4f6fb;cursor:pointer;font-size:14.5px}
#insDlg button:hover{border-color:var(--acc)}
#pgDlg{position:fixed;inset:0;background:rgba(10,18,35,.45);display:none;align-items:center;justify-content:center;z-index:50}
#pgDlg .box{background:#fff;border-radius:14px;padding:20px 24px;box-shadow:0 12px 40px rgba(0,0,0,.35);width:400px;max-width:92vw;text-align:left}
#pgDlg button{padding:10px;border-radius:9px;border:1px solid var(--line);background:#f4f6fb;cursor:pointer;font-size:14.5px}
#pgDlg button:hover{border-color:var(--acc)}
.pgsec{margin:12px 0}
.pgrad{font-size:14px;font-weight:600;display:block;cursor:pointer}
.pgrow{margin:6px 0 6px 24px;font-size:13.5px}
#pgDlg input[type=number],#pgDlg input[type=text]{padding:6px 8px;border-radius:7px;border:1px solid var(--line);font-size:13.5px;background:#fff}
#pagebar button{background:#fff;border:1px solid var(--line);border-radius:8px;padding:6px 11px;cursor:pointer;font-size:13.5px}
#pagebar button:hover{border-color:var(--acc)}
#pagebar .qa{font-weight:600}
#pageScroll{overflow:auto;flex:1;text-align:center;padding:18px}
.topbar .logo img{width:36px;height:36px;border-radius:9px;display:block}.logo{font-size:24px}.topbar h1{font-size:19px;margin:0;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif;letter-spacing:.01em}.topbar .doc{margin-left:auto;font-size:13px;color:#d7e4ff;text-align:right}
.tabs{display:flex;gap:2px;background:#eceff7;padding:6px 10px 0;border-bottom:1px solid var(--line);flex-wrap:wrap}
.tabs button{border:1px solid transparent;border-bottom:none;background:transparent;padding:6px 13px;font-size:14px;cursor:pointer;border-radius:8px 8px 0 0;color:var(--ink);text-transform:uppercase;letter-spacing:.02em}
.tabs button.on{background:var(--rib);border-color:var(--line);font-weight:700;box-shadow:inset 0 -3px 0 var(--acc)}
.ribbon{background:var(--rib);border-bottom:2px solid var(--line);padding:10px 14px;display:none;flex-wrap:wrap;gap:0;align-items:stretch;box-shadow:0 2px 6px rgba(20,30,70,.06)}
.ribbon.on{display:flex}
.grp{display:flex;flex-direction:column;gap:6px;min-width:0;padding:0 10px;border-right:1px solid var(--line)}
.grp:last-child{border-right:none}
.grp .cap{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em;border-top:1px solid var(--line);padding-top:4px;text-align:center}
.bigbtn{display:flex;flex-direction:column;align-items:center;gap:3px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:6px 10px;transition:all .15s ease;box-shadow:0 1px 2px rgba(15,23,42,.06);cursor:pointer;font-size:13px;min-width:86px}
.bigbtn:hover{border-color:var(--az);background:#EFF6FF;transform:translateY(-1px);box-shadow:0 4px 10px rgba(30,64,175,.15)}.bigbtn .ic{font-size:18px}
.rowbtns{display:flex;gap:8px;flex-wrap:wrap}
input[type=text],input[type=password],textarea{padding:7px 9px;border-radius:8px;border:1px solid var(--line);font-size:13.5px;width:230px;background:#fff}
textarea{width:330px}
label{font-size:12px;color:var(--mut)}
main{display:grid;grid-template-columns:150px 1fr 250px;gap:0;flex:1;min-height:0}
#thumbs{background:#eceff3;overflow-y:auto;overflow-x:hidden;padding:10px 8px;text-align:center}
#thumbs img{width:110px;margin:0 auto 8px;display:block;border:3px solid transparent;border-radius:4px;cursor:pointer;background:#fff;box-shadow:0 1px 5px rgba(0,0,0,.2)}
#thumbs img.sel{border-color:var(--az)}
.ptabs{display:flex;gap:4px;justify-content:center;margin-bottom:8px}
.ptabs button{border:1px solid var(--line);background:#fff;border-radius:6px;padding:4px 10px;font-size:12px;cursor:pointer}
.ptabs button.on{background:var(--az);color:#fff;border-color:var(--az)}
#tocList div{padding:5px 6px;cursor:pointer;border-radius:5px;color:var(--ink)}
#tocList div:hover{background:#e7ebff}
#thumbs .tnum{font-size:11px;color:var(--mut);margin:-4px 0 8px}
#viewer{display:flex;flex-direction:column;overflow:hidden;background:#C9CED6;padding:0}
#pageImg{max-width:100%;background:#fff;box-shadow:0 8px 32px rgba(10,20,50,.35)}
#side{background:var(--panel);border-left:1px solid var(--line);padding:14px;overflow-y:auto;font-size:13.5px}
#side h3{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
#infoBox{white-space:pre-wrap;color:#334;line-height:1.55}
.nav{display:flex;gap:6px;align-items:center}
.nav button{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 12px;cursor:pointer;font-size:14px}
.statusbar{display:flex;gap:14px;align-items:center;background:var(--panel);border-top:1px solid var(--line);padding:8px 16px;font-size:13.5px;position:sticky;bottom:0}
#status.ok{color:var(--ok)} #status.bad{color:var(--err)}
a.dl{display:inline-block;padding:7px 14px;background:var(--ok);color:#fff;border-radius:8px;text-decoration:none;font-weight:600}
.empty{color:var(--mut);font-size:16px;margin-top:70px;line-height:1.7}
.wide{flex-basis:100%}
#bMenu{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.55);color:#fff;border-radius:8px;padding:6px 12px;cursor:pointer;font-size:13px;white-space:nowrap}
#bMenu:hover{background:rgba(255,255,255,.28)}
#pagesBox{position:relative}
#hlBox{position:absolute;border:2px solid var(--acc);background:rgba(232,134,46,.16);pointer-events:none;z-index:5;border-radius:2px}
#pagebar button.mini{padding:2px 7px;font-size:12px}
#stampMark{position:absolute;font-size:26px;line-height:1;z-index:6;cursor:move;transform:translate(-4px,-24px);filter:drop-shadow(0 1px 2px rgba(0,0,0,.55));user-select:none;touch-action:none}
.qa:disabled{opacity:.45;cursor:default}
select{padding:6px 8px;border-radius:8px;border:1px solid var(--line);font-size:13px;background:#fff}
#editBar{display:none;align-items:center;gap:8px;background:#fff7ea;border-bottom:2px solid var(--acc);padding:8px 12px;font-size:13.5px}
#editBar input{flex:1;width:auto}
#editBar button{background:#fff;border:1px solid var(--line);border-radius:8px;padding:7px 13px;cursor:pointer;font-size:13.5px;font-weight:600}
#editBar button:hover{border-color:var(--acc)}
#editBar #editOk{background:var(--ok);color:#fff;border-color:var(--ok)}
.bigbtn.activo{border-color:var(--acc);background:#fff3e2;box-shadow:0 0 0 2px var(--acc) inset}
.tabs button{font-family:'Plus Jakarta Sans','Segoe UI',sans-serif;font-weight:600}
.grp .cap{font-family:'Plus Jakarta Sans',sans-serif;font-weight:700}
input:focus,textarea:focus{border-color:var(--az);outline:2px solid rgba(30,64,175,.25);outline-offset:0}
#thumbs::-webkit-scrollbar,#pageScroll::-webkit-scrollbar{width:10px;height:10px}
#thumbs::-webkit-scrollbar-thumb,#pageScroll::-webkit-scrollbar-thumb{background:#B6C2D2;border-radius:6px;border:2px solid transparent;background-clip:content-box}
#dropMsg h2{font-family:'Plus Jakarta Sans','Segoe UI',sans-serif}
.tabs button[data-t="inicio"].on{background:var(--acc);color:#fff}
#qpDel{color:#b91c1c}
#mgDlg,#svDlg,#pwDlg{position:fixed;inset:0;background:rgba(10,18,35,.45);display:none;align-items:center;justify-content:center;z-index:50}
#mgDlg .box,#svDlg .box,#pwDlg .box{background:#fff;border-radius:14px;padding:20px 24px;box-shadow:0 12px 40px rgba(0,0,0,.35);width:430px;max-width:94vw;text-align:left;max-height:88vh;overflow:auto}
#mgDlg button,#svDlg button,#pwDlg button{padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:#f4f6fb;cursor:pointer;font-size:14px}
#mgDlg button:hover,#svDlg button:hover,#pwDlg button:hover{border-color:var(--acc)}
.mgcard{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin:7px 0;background:#fbfcfe}
.mgnum{background:var(--az);color:#fff;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex:none}
.mgname{flex:1;font-size:13.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mgpg{font-size:12px;color:var(--mut);flex:none}
.mgbtn{padding:4px 8px !important;font-size:13px !important}
#dlDlg{position:fixed;inset:0;background:rgba(10,18,35,.45);display:none;align-items:center;justify-content:center;z-index:60}
#dlDlg .box{background:#fff;border-radius:14px;padding:20px 24px;box-shadow:0 12px 40px rgba(0,0,0,.35);width:400px;max-width:92vw;text-align:left}
#dlDlg button{padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:#f4f6fb;cursor:pointer;font-size:14px}
#dlDlg a.dl{display:block;text-align:center;padding:11px 14px;font-size:15px}
#side{position:relative}
#sideMin{position:absolute;top:6px;right:8px;width:26px;height:26px;border-radius:7px;border:1px solid var(--line);background:#fff;color:var(--mut);cursor:pointer;font-size:15px;line-height:1;padding:0}
#sideMin:hover{color:var(--ink);border-color:var(--acc)}
#sideTab{position:fixed;right:0;top:50%;transform:translateY(-50%);z-index:45;background:var(--navy);color:#fff;border:none;border-radius:10px 0 0 10px;padding:12px 6px;cursor:pointer;font-size:14px;box-shadow:0 4px 14px rgba(0,0,0,.25)}
.mgcard{cursor:grab}
.mgcard.drag{opacity:.45}
.mgcard.over{outline:2px dashed var(--acc);outline-offset:-2px}
</style></head><body>
<div class="topbar"><div class="logo"><img id="logoImg" alt="Aven PDF" src="data:image/png;base64,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"></div><h1>Aven PDF <span class="ver">v1.4</span></h1>
<button id="bMenu" title="Oculta las opciones de arriba para ver el PDF mas grande">▲ Ocultar menú</button>
</div>
<div class="tabs" id="tabs">
<button data-t="inicio" class="on">📁 Archivo</button>
<button data-t="crear">✨ Crear</button>
<button data-t="paginas">📄 Páginas</button>
<button data-t="convertir">🔄 Convertir</button>
<button data-t="editar">✏️ Editar</button>
<button data-t="proteger">🔒 Proteger</button>
<button data-t="firmar">✍️ Firmar</button>
<button data-t="formularios">🧾 Formularios</button>
</div>
<div class="ribbon on" id="tab-inicio">
  <div class="grp"><div class="rowbtns">
    <label class="bigbtn" id="bOpenLbl"><span class="ic">📂</span>Abrir PDF<input type="file" id="file" accept="application/pdf" hidden></label>
    <button class="bigbtn" id="bDownload" disabled><span class="ic">⬇</span>Descargar PDF</button>
    <button class="bigbtn" id="bSave" disabled><span class="ic">💾</span>Guardar cambios</button>
    <button class="bigbtn" id="bClose" disabled><span class="ic">✖</span>Cerrar documento</button>
  </div></div>
  <div class="grp"><label>Contraseña del PDF (si tiene)</label>
    <input type="password" id="pw" placeholder="••••••">
    <button class="bigbtn" id="bPwSet"><span class="ic">🔒</span>Adherir al PDF</button>
  </div>
</div>
<div class="ribbon" id="tab-crear">
  <div class="grp"><label>Imágenes (fotos o escaneos)</label>
    <input type="file" id="imgs" accept="image/*" multiple>
    <button class="bigbtn" id="bImgPdf"><span class="ic">🖼️</span>PDF desde imágenes</button>
  </div>
  <div class="grp"><input type="text" id="txtTitle" placeholder="Título del documento">
    <textarea id="txtBody" rows="3" placeholder="Escribe o pega el texto…"></textarea>
    <button class="bigbtn" id="bTxtPdf"><span class="ic">📝</span>PDF desde texto</button>
  </div>
</div>
<div class="ribbon" id="tab-paginas">
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bExtract"><span class="ic">✂️</span>Extraer</button>
    <button class="bigbtn" id="bSplit"><span class="ic">🧩</span>Dividir (ZIP)</button>
    <button class="bigbtn" id="bDel"><span class="ic">🗑️</span>Borrar</button>
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bRotL"><span class="ic">↩️</span>Girar −90°</button>
    <button class="bigbtn" id="bRotR"><span class="ic">↪️</span>Girar +90°</button>
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bMerge"><span class="ic">🔗</span>Unir PDF…</button>
  </div></div>
</div>
<div class="ribbon" id="tab-convertir">
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bWord"><span class="ic"><svg width="27" height="27" viewBox="0 0 24 24"><path d="M6 2h8l4 4v16H6z" fill="#185ABD"/><path d="M14 2l4 4h-4z" fill="#7FB2F0"/><text x="11.8" y="18.6" font-size="10.5" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="Arial, sans-serif">W</text></svg></span>a Word</button>
    <button class="bigbtn" id="bExcel"><span class="ic"><svg width="27" height="27" viewBox="0 0 24 24"><path d="M6 2h8l4 4v16H6z" fill="#107C41"/><path d="M14 2l4 4h-4z" fill="#9AD8B5"/><path d="M8.6 13.2h9.2M8.6 17h9.2M13.2 10.4v9.4" stroke="#ffffff" stroke-width="0.8" opacity="0.5"/><text x="11.4" y="10.6" font-size="8.6" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="Arial, sans-serif">X</text></svg></span>a Excel</button>
    <button class="bigbtn" id="bToPng"><span class="ic">🖼️</span>a imágenes PNG</button>
    <button class="bigbtn" id="bToTxt"><span class="ic">🔤</span>a texto</button>
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bOcrTxt"><span class="ic">👁️</span>OCR: leer escaneado</button>
    <button class="bigbtn" id="bOcrPdf"><span class="ic">🔎</span>OCR: PDF buscable</button>
  </div></div>
  <div class="grp wide"><label>Texto resultante</label>
    <textarea id="txtOut" rows="4" style="width:100%" placeholder="Aquí aparece el texto extraído u OCR…" readonly></textarea>
  </div>
</div>
<div class="ribbon" id="tab-editar">
  <div class="grp"><button class="bigbtn" id="bEditMode"><span class="ic">✏️</span>Editar sobre el PDF</button>
    <div style="font-size:12px;color:var(--mut);max-width:180px;line-height:1.45">Actívalo y haz <b>clic sobre cualquier línea</b> del documento para corregirla ahí mismo.</div>
  </div>
  <div class="grp"><input type="text" id="noteText" placeholder="Ej. REVISADO">
    <div class="rowbtns"><select id="noteScope" title="Alcance del estampado"><option value="page">En esta página</option><option value="all">En todas las páginas</option></select>
    <select id="notePos" title="Ubicación del texto"><option value="centro">Centro</option><option value="supcentro">Arriba al centro</option><option value="supizq">Arriba a la izquierda</option><option value="supder">Arriba a la derecha</option><option value="infcentro">Abajo al centro</option><option value="infizq">Abajo a la izquierda</option><option value="infder">Abajo a la derecha</option><option value="marca">📍 Donde yo marque</option></select></div>
    <div class="rowbtns"><button class="bigbtn" id="bNote"><span class="ic">🏷️</span>Estampar texto</button>
    <button class="bigbtn" id="bMark" title="Actívalo y haz clic en la página para dejar la flecha donde irá el texto; la flecha se puede arrastrar"><span class="ic">📍</span>Marcar posición</button></div>
  </div>
  <div class="grp"><input type="text" id="wmText" placeholder="Ej. CONFIDENCIAL">
    <div class="rowbtns"><button class="bigbtn" id="bWm"><span class="ic">💧</span>Marca de agua</button>
    <label class="bigbtn" title="Usa una imagen (un logo o un sello) como marca de agua en todas las páginas"><span class="ic">🖼️</span>Imagen de marca<input type="file" id="wmImg" accept="image/*" hidden></label></div>
  </div>
  <div class="grp"><input type="text" id="findTxt" placeholder="Texto actual">
    <input type="text" id="replTxt" placeholder="Texto nuevo">
    <button class="bigbtn" id="bRepl"><span class="ic">🔁</span>Buscar y reemplazar</button>
  </div>
</div>
<div class="ribbon" id="tab-proteger">
  <div class="grp"><input type="password" id="newPw" placeholder="Contraseña nueva">
    <button class="bigbtn" id="bEnc"><span class="ic">🔐</span>Proteger (AES-256)</button>
  </div>
  <div class="grp"><button class="bigbtn" id="bDec"><span class="ic">🔓</span>Quitar contraseña</button>
  </div>
  <div class="grp"><button class="bigbtn" id="bComp"><span class="ic">🗜️</span>Comprimir</button>
  </div>
</div>
<div class="ribbon" id="tab-firmar">
  <div class="grp"><input type="text" id="signName" placeholder="Tu nombre">
    <button class="bigbtn" id="bStamp"><span class="ic">🖋️</span>Sello visual</button>
  </div>
  <div class="grp"><input type="text" id="certName" placeholder="Tu nombre completo">
    <input type="password" id="certPw" placeholder="Contraseña del certificado">
    <button class="bigbtn" id="bCert"><span class="ic">📜</span>Crear mi certificado</button>
  </div>
  <div class="grp"><input type="file" id="pfxFile" accept=".pfx,.p12">
    <input type="password" id="pfxPw" placeholder="Contraseña del certificado">
    <button class="bigbtn" id="bSign"><span class="ic">✍️</span>Firmar digitalmente</button>
  </div>
</div>
<div class="ribbon" id="tab-formularios">
  <div class="grp"><button class="bigbtn" id="bFields"><span class="ic">🧾</span>Ver campos</button>
  </div>
  <div class="grp wide"><div id="fieldsBox" style="font-size:13.5px">Aquí aparecen los campos si el PDF es un formulario.</div>
  </div>
</div>
<main>
<div id="thumbs"><div class="ptabs"><button id="ptPages" class="on">Páginas</button><button id="ptMarks">Marcadores</button></div><div id="thumbList"></div><div id="tocList" style="display:none;text-align:left;font-size:13px"></div></div>
<div id="viewer">
<div id="pagebar">
<div class="pb"><button id="zout">−</button><span style="font-size:13px">Zoom</span><button id="zin">+</button>
<button id="qpDl" title="Descargar el PDF actual con nombre de versión (…_AvenPDF_v01, v02…)">⬇ Descargar</button>
<button id="qpSave" title="Guardar cambios: reemplazar el archivo original o guardar una copia nueva">💾 Guardar</button></div>
<div class="pb c"><button id="prev">◀</button><span id="pgLabel">—</span><button id="next">▶</button></div>
<div class="pb r">
<button class="qa" id="qpIns" title="Insertar otro PDF junto a esta página">➕ Insertar PDF</button>
<input type="file" id="qpInsFile" accept="application/pdf" hidden>
<button class="qa" id="qpRotL" title="Girar esta página a la izquierda">⤺ Izquierda</button>
<button class="qa" id="qpRotR" title="Girar esta página a la derecha">⤼ Derecha</button>
<button class="qa" id="qpExt" title="Descargar solo esta página como PDF">✂ Extraer</button>
<button class="qa" id="qpDel" title="Borrar únicamente esta página">✖ Borrar esta página</button>
<button class="qa" id="qpUndo" title="Deshacer el último cambio (Ctrl+Z)">↩ Deshacer</button>
<button class="qa" id="qpRedo" title="Rehacer el cambio deshecho (Ctrl+Y)">↪ Rehacer</button></div>
</div>
<div id="mgDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🔗 Unir archivos PDF</div>
<div style="font-size:13px;color:var(--mut)">Añade los PDF, arrástralos para ordenarlos y confirma. Se unen en ese orden exacto.</div>
<div id="mgList" style="margin-top:8px"></div>
<div style="margin-top:10px"><label class="bigbtn" style="display:inline-flex"><span class="ic">➕</span>Añadir archivos…<input type="file" id="mgFiles" accept="application/pdf" multiple hidden></label></div>
<div id="mgPosWrap" style="margin-top:12px;font-size:14px;display:none">
<div style="font-weight:600;margin-bottom:5px">Ya tienes un documento abierto. Los nuevos van:</div>
<label style="display:block;cursor:pointer;margin:3px 0"><input type="radio" name="mgPos" value="end" checked> Al final del documento actual</label>
<label style="display:block;cursor:pointer;margin:3px 0"><input type="radio" name="mgPos" value="start"> Al principio del documento actual</label>
</div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="mgOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Unir ahora</button><button id="mgCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="svDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">💾 Guardar cambios</div>
<div style="font-size:13.5px;color:var(--mut)">El documento tiene cambios sin guardar. Elige cómo guardarlos:</div>
<div style="margin-top:12px;display:flex;flex-direction:column;gap:8px">
<button id="svReplace" style="font-weight:700">Reemplazar el archivo original</button>
<span id="svNote" style="font-size:12.5px;color:var(--mut)"></span>
<button id="svCopy">Guardar como copia nueva (nombre_AvenPDF_v01)</button>
<button id="svCancel">Cancelar</button>
</div></div></div>
<div id="pwDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🔒 Contraseña adherida al PDF</div>
<div style="font-size:14px;line-height:1.55">Desde ahora este PDF pedirá la contraseña para abrirse.<br><b>Recuérdala o anótala en un lugar seguro:</b> si la olvidas, no habrá forma de abrir el documento.</div>
<div style="margin-top:14px"><button id="pwOkBtn" style="width:100%;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Entendido</button></div>
</div></div>
<div id="dlDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">⬇ Descarga lista</div>
<div id="dlName" style="font-weight:600;font-size:14.5px;word-break:break-all"></div>
<div id="dlMsg" style="font-size:13.5px;color:var(--mut);margin-top:3px"></div>
<div id="dlSlot" style="margin-top:13px"></div>
<div style="margin-top:10px"><button id="dlClose" style="width:100%">Cerrar</button></div>
</div></div>
<div id="pgDlg"><div class="box">
<div id="pgTitle" style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">Páginas</div>
<div id="pgHint" style="font-size:13px;color:var(--mut);margin-bottom:6px"></div>
<div id="pgSecFixed" class="pgsec"><label class="pgrad"><input type="radio" name="pgMode" value="fixed" checked> En partes de un tamaño fijo:</label>
<div class="pgrow">Cada <input type="number" id="pgN" value="1" min="1" style="width:70px"> página(s) <span style="color:var(--mut)">(de 1 en 1, 2 en 2, 3 en 3…)</span></div></div>
<div id="pgSecRanges" class="pgsec"><label class="pgrad"><input type="radio" name="pgMode" value="ranges"> Por rangos (cada rango = un PDF):</label>
<div class="pgrow"><input type="text" id="pgRanges" placeholder="1-3, 5-6" style="width:210px"></div></div>
<div id="pgSecRange" class="pgsec"><label class="pgrad"><input type="radio" name="pgMode" value="range" checked> Un rango:</label>
<div class="pgrow">Desde <input type="number" id="pgFrom" value="1" min="1" style="width:70px"> hasta <input type="number" id="pgTo" value="1" min="1" style="width:70px"> <span id="pgTotal" style="color:var(--mut)"></span></div></div>
<div id="pgSecList" class="pgsec"><label class="pgrad"><input type="radio" name="pgMode" value="list"> Páginas sueltas:</label>
<div class="pgrow"><input type="text" id="pgList" placeholder="2, 5, 7" style="width:210px"></div></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="pgOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Aceptar</button><button id="pgCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="insDlg"><div class="box"><div style="font-size:16px;font-weight:600;margin-bottom:6px">¿Dónde inserto el otro PDF?</div>
<div style="font-size:13.5px;color:var(--mut)">Elige la página y si el otro PDF va antes o después de ella</div>
<div style="margin:10px 0;font-size:14px">Página: <input type="number" id="insPage" value="1" min="1" style="width:72px;padding:6px 8px;border-radius:7px;border:1px solid var(--line)"> <span id="insTotal" style="color:var(--mut);font-size:12.5px"></span></div>
<button id="insBefore">⬆ Antes de esa página</button>
<button id="insAfter">⬇ Después de esa página</button>
<button id="insCancel">Cancelar</button></div></div>
<div id="editBar"><span>✏️ <b>Editando línea:</b></span><input type="text" id="editInput"><button id="editOk">✔ Aplicar</button><button id="editCancel">Cancelar</button></div>
<div id="pageScroll">
<div id="pagesBox"></div>
<div class="empty" id="emptyMsg">📂 Abre un PDF con el botón «Abrir PDF» de la pestaña Archivo<br>o arrastra el archivo hasta aquí.<br><span style="font-size:13.5px">Créditos: Luis Aven</span></div>
</div>
</div>
<aside id="side"><button id="sideMin" title="Minimizar: ocultar los datos del documento">—</button><h3>Datos del documento</h3><div id="infoBox">Sin documento cargado.</div></aside>
<button id="sideTab" title="Mostrar los datos del documento" style="display:none">❮</button>
</main>
<div class="statusbar"><span id="status">Listo.</span></div>

<script>
let cur=null, curName="documento.pdf", page=0, pages=0, zoom=1.4;
let dirty=false, dlVer=0, fileHandle=null;
const $=id=>document.getElementById(id);
$("favIco").href=$("logoImg").src;
document.querySelectorAll("#tabs button").forEach(b=>b.onclick=()=>{
  document.querySelectorAll("#tabs button").forEach(x=>x.classList.remove("on")); b.classList.add("on");
  document.querySelectorAll(".ribbon").forEach(r=>r.classList.remove("on"));
  $("tab-"+b.dataset.t).classList.add("on");
});
function gotoTab(t){ document.querySelector(`#tabs button[data-t="${t}"]`).click(); return true; }
function status(msg,ok=true){const s=$("status");s.textContent=msg;s.className=ok?"ok":"bad";}
function readB64(f){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result.split(",")[1]);r.onerror=rej;r.readAsDataURL(f);});}
async function call(path,payload){
  const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const j=await r.json(); if(!r.ok||j.error) throw new Error(j.error||("HTTP "+r.status)); return j;
}
function b64ToBlob(b64,mime="application/pdf"){
  const bin=atob(b64),arr=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);
  return new Blob([arr],{type:mime});
}
let dlNote="";
function saveB64(b64,name,mime="application/pdf"){
  const a=document.createElement("a");a.href=URL.createObjectURL(b64ToBlob(b64,mime));a.download=name;a.className="dl";a.textContent="⬇ Descargar";
  $("dlName").textContent=name;
  $("dlMsg").textContent=dlNote||"Tu archivo está listo."; dlNote="";
  const slot=$("dlSlot"); slot.innerHTML=""; slot.appendChild(a);
  $("dlDlg").style.display="flex";
}
$("dlClose").onclick=()=>{ $("dlDlg").style.display="none"; };
function versionedName(){ dlVer++; const base=curName.replace(/\.pdf$/i,""); return base+"_AvenPDF_v"+String(dlVer).padStart(2,"0")+".pdf"; }
function downloadCurrent(){ if(!cur){status("Primero abre un PDF.",false); return;} const nm=versionedName(); dlNote="Copia v"+String(dlVer).padStart(2,"0")+" del documento: el archivo original no se tocó."; saveB64(cur,nm); status("Copia v"+String(dlVer).padStart(2,"0")+" lista para descargar ✔"); }
let lastToc=[];
function clearDownloads(){ const d=$("dlDlg"); if(d)d.style.display="none"; }
function renderToc(){
  const box=$("tocList"); box.innerHTML="";
  if(!lastToc.length){ box.innerHTML="<div style='color:var(--mut)'>Este PDF no trae marcadores.</div>"; return; }
  lastToc.forEach(([lv,t,pg])=>{ const d=document.createElement("div");
    d.textContent=t; d.style.paddingLeft=(6+(lv-1)*14)+"px"; d.title="Ir a la página "+pg;
    d.onclick=()=>{ gotoPage(Math.min(pg-1,pages-1)); };
    box.appendChild(d); });
}
let histU=[], histR=[], histJump=false;
function updHist(){ const u=$("qpUndo"),r=$("qpRedo"); if(u)u.disabled=!histU.length; if(r)r.disabled=!histR.length; }
async function setCurrent(b64,name,stayPage){
  const prevPage=page;
  if(cur && b64!==cur && !histJump){ histU.push({pdf:cur,name:curName,page:prevPage}); if(histU.length>25)histU.shift(); histR=[]; }
  clearDownloads();
  cur=b64; if(name)curName=name; page=stayPage?prevPage:0;
  const info=await call("/api/info",{pdf:cur,password:$("pw").value}); pages=info.pages;
  if(page>=pages)page=pages-1; if(page<0)page=0;
  lastToc=info.toc||[]; renderToc();
  $("infoBox").textContent=`Archivo: ${curName}\nPáginas: ${info.pages}\nTamaño: ${info.size_kb} KB\nTítulo: ${info.title||"—"}\nAutor: ${info.author||"—"}\nCreador: ${info.creator||"—"}\nMarcadores: ${info.bookmarks}${info.encrypted?"\n🔒 Protegido con contraseña":""}`;
  $("bDownload").disabled=false; $("bClose").disabled=false; $("bSave").disabled=false; dirty=true;
  await renderAll(); await buildThumbs(); gotoPage(page,false); updHist();
}
let lastPix=null;
let renderGen=0;
async function renderAll(){
  if(!cur)return;
  const gen=++renderGen;
  const box=$("pagesBox"); box.innerHTML=""; clearStampMark();
  const n=Math.min(pages,120);
  for(let i=0;i<n;i++){
    const j=await call("/api/render",{pdf:cur,page:i,zoom,password:$("pw").value});
    if(gen!==renderGen)return;
    if(i===0)lastPix={w:j.w,h:j.h,zoom};
    const im=document.createElement("img"); im.className="cpage"; im.src="data:image/png;base64,"+j.png; im.dataset.i=i;
    im.onclick=(ev)=>{ page=i; syncLabel(); if(editMode) pickLine(ev,im,i); else if(markMode) setStampMark(ev,im); };
    box.appendChild(im);
  }
  if(editMode) box.querySelectorAll(".cpage").forEach(x=>x.style.cursor="text");
  if(pages>120) status("Documento muy grande: muestro las primeras 120 páginas en el visor.");
  if(stampPt) drawStampMark();
  syncLabel();
  requestAnimationFrame(()=>gotoPage(page,false));
}
function syncThumbs(){ document.querySelectorAll("#thumbList .titem").forEach((w,k)=>{ const im=w.querySelector("img"); if(im)im.classList.toggle("sel",k===page); }); }
function syncLabel(){
  $("pgLabel").textContent=pages?`Página ${page+1} de ${pages}`:"—";
  document.querySelectorAll(".cpage").forEach(im=>{ im.style.outline=(+im.dataset.i===page)?"3px solid var(--acc)":"none"; });
  syncThumbs();
}
function gotoPage(i,smooth=true){
  if(!pages)return; page=Math.max(0,Math.min(pages-1,i));
  const el=document.querySelector(`.cpage[data-i="${page}"]`);
  if(el) el.scrollIntoView({block:"start",behavior:smooth?"smooth":"auto"});
  syncLabel();
}
let scrollTick=false;
document.addEventListener("DOMContentLoaded",()=>{});
let syncing=false;
function attachScrollSync(){
  const sc=$("pageScroll"); if(!sc||sc.dataset.sync)return; sc.dataset.sync="1";
  sc.addEventListener("scroll",()=>{ if(scrollTick)return; scrollTick=true;
    requestAnimationFrame(()=>{ scrollTick=false; if(!pages)return;
      const top=sc.getBoundingClientRect().top+70; let curI=0;
      document.querySelectorAll(".cpage").forEach(im=>{ if(im.getBoundingClientRect().top<=top) curI=+im.dataset.i; });
      if(curI!==page){ page=curI; syncLabel(); }
    });
  });
}
let thumbGen=0;
function renumberThumbs(){ document.querySelectorAll("#thumbList .titem").forEach((w,k)=>{ w.dataset.idx=k; const n=w.querySelector(".tnum"); if(n)n.textContent=k+1; }); }
async function buildThumbs(){
  const gen=++thumbGen;
  const box=$("thumbList"); box.innerHTML="";
  const n=Math.min(pages,60);
  for(let i=0;i<n;i++){
    const j=await call("/api/render",{pdf:cur,page:i,zoom:0.22,password:$("pw").value});
    if(gen!==thumbGen)return;
    const im=document.createElement("img"); im.src="data:image/png;base64,"+j.png;
    const num=document.createElement("div"); num.className="tnum"; num.textContent=(i+1);
    const wrap=document.createElement("div"); wrap.className="titem"; wrap.draggable=true; wrap.dataset.idx=i;
    wrap.appendChild(im); wrap.appendChild(num); box.appendChild(wrap);
    im.onclick=()=>{ const idx=[...box.querySelectorAll(".titem")].indexOf(wrap); if(idx>=0)gotoPage(idx); };
    wrap.addEventListener("dragstart",e=>{ e.dataTransfer.setData("text/plain",String([...box.querySelectorAll(".titem")].indexOf(wrap))); wrap.style.opacity=".45"; });
    wrap.addEventListener("dragend",()=>{ wrap.style.opacity="1"; document.querySelectorAll(".titem").forEach(t=>t.classList.remove("dragov")); });
    wrap.addEventListener("dragover",e=>{ e.preventDefault(); wrap.classList.add("dragov"); });
    wrap.addEventListener("dragleave",()=>wrap.classList.remove("dragov"));
    wrap.addEventListener("drop",async e=>{ e.preventDefault(); wrap.classList.remove("dragov");
      const from=+e.dataTransfer.getData("text/plain");
      const to=[...box.querySelectorAll(".titem")].indexOf(wrap);
      if(from===to||isNaN(from)||to<0)return;
      const order=Array.from({length:pages},(_,k)=>k);
      order.splice(to,0,order.splice(from,1)[0]);
      run(async()=>{ const j=await call("/api/reorder",{pdf:cur,order});
        await setCurrent(j.pdf,curName); page=to; gotoPage(to,false); syncLabel();
        status(`Página movida a la posición ${to+1} ✔ (arrastra las miniaturas para reordenar)`); });
    });
  }
  if(pages>60){const d=document.createElement("div");d.className="tnum";d.textContent="…miniaturas hasta la 60";box.appendChild(d);}
  renumberThumbs(); syncThumbs();
  attachScrollSync();
}
async function need(){ if(!cur){status("Primero abre un PDF (pestaña Inicio).",false); gotoTab("inicio"); throw new Error("sin archivo");} }
async function run(fn,msg){ try{ clearDownloads(); status("Procesando…"); await fn(); if(msg)status(msg);}catch(e){ status("Error: "+e.message,false);} }
function wipeViewer(msg){
  $("pagesBox").innerHTML=""; $("thumbList").innerHTML=""; $("tocList").innerHTML="";
  $("pgLabel").textContent="—"; $("emptyMsg").style.display="block"; status(msg||"Listo.");
}
$("file").addEventListener("change",async e=>{ const f=e.target.files[0]; if(!f)return;
  if(!confirmarReemplazo()){ e.target.value=""; return; }
  fileHandle=null; wipeViewer("Cargando "+f.name+"…");
  run(async()=>{ await setCurrent(await readB64(f), f.name); dirty=false; dlVer=0; status("PDF cargado ✔ (el anterior se cerró)"); }); });
document.getElementById('bOpenLbl').addEventListener("click",async e=>{
  if(!window.showOpenFilePicker) return;
  e.preventDefault();
  if(!confirmarReemplazo()) return;
  try{
    const [h]=await window.showOpenFilePicker({types:[{description:"PDF",accept:{"application/pdf":[".pdf"]}}],multiple:false});
    const f=await h.getFile(); fileHandle=h;
    wipeViewer("Cargando "+f.name+"…");
    run(async()=>{ await setCurrent(await readB64(f), f.name); dirty=false; dlVer=0; status("PDF cargado ✔ (con Guardar podrás reemplazar el original)"); });
  }catch(err){ }
});
$("bClose").onclick=()=>{ if(cur && !confirm("¿Cerrar el documento? Los cambios que no hayas descargado se perderán."))return; cur=null; pages=0; page=0; lastToc=[];
  $("infoBox").textContent="Sin documento cargado."; $("bDownload").disabled=true; $("bClose").disabled=true; $("bSave").disabled=true; fileHandle=null; dirty=false; dlVer=0;
  histU=[]; histR=[]; updHist(); clearDownloads(); wipeViewer("Documento cerrado."); };
$("ptPages").onclick=()=>{ $("ptPages").classList.add("on"); $("ptMarks").classList.remove("on"); $("thumbList").style.display="block"; $("tocList").style.display="none"; };
$("ptMarks").onclick=()=>{ $("ptMarks").classList.add("on"); $("ptPages").classList.remove("on"); $("thumbList").style.display="none"; $("tocList").style.display="block"; };
$("qpDel").onclick=()=>run(async()=>{ await need(); if(pages<=1)throw new Error("Es la única página");
  const j=await call("/api/delete_pages",{pdf:cur,pages:String(page+1)});
  await setCurrent(j.pdf,curName,true); status("Esta página fue borrada ✔ (solo esa hoja)"); });
$("qpRotL").onclick=()=>run(async()=>{ await need();
  const j=await call("/api/rotate",{pdf:cur,pages:String(page+1),degrees:-90});
  await setCurrent(j.pdf,curName,true); status("Página girada a la izquierda ✔"); });
$("qpRotR").onclick=()=>run(async()=>{ await need();
  const j=await call("/api/rotate",{pdf:cur,pages:String(page+1),degrees:90});
  await setCurrent(j.pdf,curName,true); status("Página girada a la derecha ✔"); });
$("qpExt").onclick=()=>run(async()=>{ await need();
  const j=await call("/api/extract",{pdf:cur,pages:String(page+1)});
  saveB64(j.pdf,"pagina_"+(page+1)+".pdf"); status("Página "+(page+1)+" lista para descargar ✔"); });
let insMode="after", insTarget=0;
$("qpIns").onclick=()=>{ if(!cur){status("Primero abre un PDF.",false); return;} $("insPage").value=page+1; $("insTotal").textContent="(el documento tiene "+pages+")"; $("insDlg").style.display="flex"; };
$("insCancel").onclick=()=>{ $("insDlg").style.display="none"; };
function insGo(mode){ const n=parseInt($("insPage").value||"0",10);
  if(!(n>=1&&n<=pages)){ status("Esa página no existe: escribe un número entre 1 y "+pages+".",false); return; }
  insMode=mode; insTarget=n-1; $("insDlg").style.display="none"; $("qpInsFile").click(); }
$("insBefore").onclick=()=>insGo("before");
$("insAfter").onclick=()=>insGo("after");
$("qpInsFile").addEventListener("change",async e=>{ const f=e.target.files[0]; if(!f)return;
  run(async()=>{ const other=await readB64(f);
    const at=(insMode==="before")?insTarget-1:insTarget;
    const j=await call("/api/insert_pdf",{pdf:cur,other,at});
    await setCurrent(j.pdf,curName,true);
    status(j.inserted+" página(s) insertadas "+(insMode==="before"?"antes":"después")+" de la página "+(insTarget+1)+" ✔"); });
  e.target.value=""; });
const viewer=$("pageScroll");
let wzT=null, wzPend=null;
$("pageScroll").addEventListener("wheel",e=>{ if(!e.ctrlKey||!cur)return; e.preventDefault();
  wzPend=(wzPend==null?zoom:wzPend)*(e.deltaY<0?1.12:0.89);
  wzPend=Math.max(0.3,Math.min(3.5,wzPend));
  if(wzT)clearTimeout(wzT);
  wzT=setTimeout(async()=>{ zoom=wzPend; wzPend=null; await renderAll(); gotoPage(page,false); },150);
},{passive:false});
viewer.addEventListener("dragover",e=>e.preventDefault());
viewer.addEventListener("drop",e=>{ e.preventDefault(); const f=e.dataTransfer.files[0]; if(!f)return;
  const item=e.dataTransfer.items&&e.dataTransfer.items[0];
  if(item&&item.getAsFileSystemHandle){ item.getAsFileSystemHandle().then(h=>{ fileHandle=(h&&h.kind==="file")?h:null; }).catch(()=>{ fileHandle=null; }); }
  else fileHandle=null;
  if(confirmarReemplazo()) run(async()=>{ await setCurrent(await readB64(f), f.name); dirty=false; dlVer=0; status("PDF cargado ✔"); }); });
async function doUndo(){ if(!histU.length){ status("No hay cambios que deshacer."); return; }
  const s=histU.pop(); histR.push({pdf:cur,name:curName,page}); histJump=true;
  await setCurrent(s.pdf,s.name,true); page=Math.max(0,Math.min(pages-1,s.page)); gotoPage(page,false); syncLabel();
  histJump=false; updHist(); status("Cambio deshecho ↩ (con Rehacer lo recuperas)"); }
async function doRedo(){ if(!histR.length){ status("No hay cambios que rehacer."); return; }
  const s=histR.pop(); histU.push({pdf:cur,name:curName,page}); histJump=true;
  await setCurrent(s.pdf,s.name,true); page=Math.max(0,Math.min(pages-1,s.page)); gotoPage(page,false); syncLabel();
  histJump=false; updHist(); status("Cambio rehecho ↪"); }
$("qpUndo").onclick=()=>run(doUndo);
$("qpRedo").onclick=()=>run(doRedo);
document.addEventListener("keydown",e=>{ const t=e.target;
  if(t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.tagName==="SELECT"||t.isContentEditable))return;
  if(!(e.ctrlKey||e.metaKey))return; const k=(e.key||"").toLowerCase();
  if(k==="z"&&!e.shiftKey){ e.preventDefault(); run(doUndo); }
  else if(k==="y"||(k==="z"&&e.shiftKey)){ e.preventDefault(); run(doRedo); } });
$("prev").onclick=()=>gotoPage(page-1);
$("next").onclick=()=>gotoPage(page+1);
$("zin").onclick=async()=>{ zoom=Math.min(3,zoom+0.2); await renderAll(); gotoPage(page,false); };
$("zout").onclick=async()=>{ zoom=Math.max(0.5,zoom-0.2); await renderAll(); gotoPage(page,false); };

let editMode=false, editSel=null;
$("bMenu").onclick=()=>{ const tabs=$("tabs"), off=tabs.style.display!=="none";
  tabs.style.display=off?"none":"";
  document.querySelectorAll(".ribbon").forEach(r=>{ r.style.display=off?"none":""; });
  $("bMenu").textContent=off?"▼ Mostrar menú":"▲ Ocultar menú";
  status(off?"Menú oculto: el PDF ocupa más pantalla. Vuelve con «▼ Mostrar menú».":"Menú visible."); };
let datosOn=true;
function setDatos(on){ datosOn=on;
  $("side").style.display=on?"":"none";
  $("sideTab").style.display=on?"none":"";
  document.querySelector("main").style.gridTemplateColumns=on?"":"150px 1fr 0px";
  status(on?"Panel de datos visible.":"Datos ocultos: el PDF se ve más ancho."); }
$("sideMin").onclick=()=>setDatos(false);
$("sideTab").onclick=()=>setDatos(true);
function confirmarReemplazo(){
  if(!cur) return true;
  return confirm("Ya hay un documento abierto ("+curName+").\n\nSi continúas, ese documento se cerrará y perderás los cambios que NO hayas descargado.\n\n¿Cerrar el actual y continuar?");
}
window.addEventListener("beforeunload",e=>{ if(cur){ e.preventDefault(); e.returnValue=""; } });
function clearHighlight(){ const h=$("hlBox"); if(h)h.remove(); }
function closeEditBar(){ $("editBar").style.display="none"; clearHighlight(); }
$("bEditMode").onclick=async()=>{ try{ await need(); }catch(e){ return; }
  editMode=!editMode; $("bEditMode").classList.toggle("activo",editMode);
  document.querySelectorAll(".cpage").forEach(im=>im.style.cursor=editMode?"text":"");
  if(!editMode){ editSel=null; closeEditBar(); status("Edición directa desactivada."); }
  else status("Edición directa ACTIVADA: haz clic sobre la línea del PDF que quieras corregir."); };
async function pickLine(ev,im,i){
  const r=im.getBoundingClientRect();
  const fx=(ev.clientX-r.left)/r.width, fy=(ev.clientY-r.top)/r.height;
  run(async()=>{ const j=await call("/api/text_at",{pdf:cur,page:i,fx,fy,password:$("pw").value});
    if(!j.found){ status("Ahí no hay texto editable: puede ser una imagen o un escaneo (para eso usa OCR).",false); return; }
    editSel={page:i,bbox:j.bbox,origin:j.origin,size:j.size,font:j.font,color:j.color,page_w:j.page_w,page_h:j.page_h};
    clearHighlight();
    const hl=document.createElement("div"); hl.id="hlBox";
    const sx=im.offsetWidth/j.page_w, sy=im.offsetHeight/j.page_h;
    hl.style.left=(im.offsetLeft+j.bbox[0]*sx)+"px"; hl.style.top=(im.offsetTop+j.bbox[1]*sy)+"px";
    hl.style.width=((j.bbox[2]-j.bbox[0])*sx)+"px"; hl.style.height=((j.bbox[3]-j.bbox[1])*sy)+"px";
    $("pagesBox").appendChild(hl);
    $("editInput").value=j.text; $("editBar").style.display="flex";
    $("editInput").focus(); $("editInput").select();
    status("Línea seleccionada: corrige el texto en la barra naranja y pulsa ✔ Aplicar."); });
}
$("editCancel").onclick=()=>{ editSel=null; closeEditBar(); status("Edición cancelada."); };
$("editInput").addEventListener("keydown",e=>{ if(e.key==="Enter")$("editOk").click(); if(e.key==="Escape")$("editCancel").click(); });
$("editOk").onclick=()=>run(async()=>{ if(!editSel)throw new Error("Primero haz clic en una línea del PDF");
  const j=await call("/api/edit_line",{pdf:cur,page:editSel.page,bbox:editSel.bbox,origin:editSel.origin,
    size:editSel.size,font:editSel.font,color:editSel.color,text:$("editInput").value,password:$("pw").value});
  editSel=null; closeEditBar();
  await setCurrent(j.pdf,"editado.pdf",true);
  status("Línea editada sobre el PDF ✔ (el documento sigue abierto, ya corregido)"); });
$("bDownload").onclick=downloadCurrent;
$("qpDl").onclick=downloadCurrent;
$("qpSave").onclick=()=>$("bSave").click();
$("bSave").onclick=()=>run(async()=>{ await need();
  if(!dirty){ status("Este documento no tiene cambios nuevos por guardar."); return; }
  $("svReplace").disabled=!fileHandle;
  $("svNote").textContent=fileHandle?"":"Sin acceso directo al archivo original en este navegador: usa «Guardar como copia nueva».";
  $("svDlg").style.display="flex"; });
$("svCancel").onclick=()=>{ $("svDlg").style.display="none"; };
$("svCopy").onclick=()=>{ $("svDlg").style.display="none"; downloadCurrent(); };
$("svReplace").onclick=()=>run(async()=>{ $("svDlg").style.display="none";
  const perm=await fileHandle.requestPermission({mode:"readwrite"});
  if(perm!=="granted")throw new Error("No diste permiso para escribir el archivo original");
  const w=await fileHandle.createWritable(); await w.write(b64ToBlob(cur)); await w.close();
  dirty=false; status("Cambios guardados en el archivo original ✔ ("+curName+")"); });
$("bPwSet").onclick=()=>run(async()=>{ await need(); const p=$("pw").value;
  if(!p)throw new Error("Escribe primero la contraseña en el campo de Acceso");
  const j=await call("/api/encrypt",{pdf:cur,password:p});
  await setCurrent(j.pdf,curName); $("pwDlg").style.display="flex"; });
$("pwOkBtn").onclick=()=>{ $("pwDlg").style.display="none"; status("Contraseña adherida ✔ El PDF la pedirá al abrirse."); };
$("bImgPdf").onclick=()=>run(async()=>{ if(!confirmarReemplazo())return; const fs=$("imgs").files; if(!fs.length)throw new Error("Elige imágenes");
  const arr=[]; for(const f of fs)arr.push(await readB64(f));
  const j=await call("/api/images_to_pdf",{images:arr}); await setCurrent(j.pdf,"desde_imagenes.pdf"); status("PDF creado desde imágenes ✔"); });
$("bTxtPdf").onclick=()=>run(async()=>{ if(!confirmarReemplazo())return; const t=$("txtBody").value; if(!t.trim())throw new Error("Escribe un texto");
  const j=await call("/api/text_to_pdf",{text:t,title:$("txtTitle").value}); await setCurrent(j.pdf,"desde_texto.pdf"); status("PDF creado desde texto ✔"); });
let pgKind=null;
function openPgDlg(kind){ pgKind=kind;
  const T={extract:["✂️ Extraer páginas","Elige qué páginas quieres sacar a un PDF nuevo.","Extraer y crear PDF"],
    del:["🗑️ Borrar páginas","Elige qué páginas quieres borrar del documento.","Borrar páginas"],
    split:["🧩 Dividir el PDF","Elige cómo quieres partir el documento en varios PDF.","Dividir y descargar ZIP"]}[kind];
  $("pgTitle").textContent=T[0]; $("pgHint").textContent=T[1]; $("pgOk").textContent=T[2];
  $("pgSecFixed").style.display=kind==="split"?"block":"none";
  $("pgSecRanges").style.display=kind==="split"?"block":"none";
  $("pgSecRange").style.display=kind==="split"?"none":"block";
  $("pgSecList").style.display=kind==="split"?"none":"block";
  document.querySelector('input[name="pgMode"][value="'+(kind==="split"?"fixed":"range")+'"]').checked=true;
  $("pgFrom").value=1; $("pgTo").value=pages; $("pgTotal").textContent="(el documento tiene "+pages+")";
  $("pgDlg").style.display="flex"; }
$("bExtract").onclick=()=>run(async()=>{ await need(); openPgDlg("extract"); });
$("bSplit").onclick=()=>run(async()=>{ await need(); openPgDlg("split"); });
$("bDel").onclick=()=>run(async()=>{ await need(); openPgDlg("del"); });
$("pgCancel").onclick=()=>{ $("pgDlg").style.display="none"; };
document.querySelectorAll("#pgDlg .pgsec input[type=text], #pgDlg .pgsec input[type=number]").forEach(inp=>{
  inp.addEventListener("focus",()=>{ const sec=inp.closest(".pgsec"); const r=sec&&sec.querySelector('input[type="radio"]'); if(r)r.checked=true; }); });
$("pgOk").onclick=()=>run(async()=>{
  const mode=document.querySelector('input[name="pgMode"]:checked').value;
  if(pgKind==="split"){
    if(mode==="fixed"){ const n=parseInt($("pgN").value||"1",10); if(!(n>=1))throw new Error("El tamaño de parte debe ser 1 o más");
      $("pgDlg").style.display="none";
      const j=await call("/api/split",{pdf:cur,mode:"fixed",n});
      saveB64(j.zip,"dividido.zip","application/zip"); status("PDF dividido en "+j.parts+" parte(s) ✔ (ZIP descargado)"); }
    else { const spec=$("pgRanges").value.trim(); if(!spec)throw new Error("Escribe los rangos, p. ej. 1-3, 5-6");
      $("pgDlg").style.display="none";
      const j=await call("/api/split",{pdf:cur,mode:"ranges",spec});
      saveB64(j.zip,"dividido.zip","application/zip"); status("PDF dividido en "+j.parts+" parte(s) ✔ (ZIP descargado)"); }
    return; }
  let spec="";
  if(mode==="range"){ const a=parseInt($("pgFrom").value||"1",10), b=parseInt($("pgTo").value||"1",10);
    if(!(a>=1&&b>=a&&b<=pages))throw new Error("Rango no válido: debe ir del 1 al "+pages+" y «desde» no puede ser mayor que «hasta»");
    spec=a+"-"+b; }
  else { spec=$("pgList").value.trim(); if(!spec)throw new Error("Escribe las páginas, p. ej. 2, 5, 7"); }
  $("pgDlg").style.display="none";
  if(pgKind==="extract"){ const j=await call("/api/extract",{pdf:cur,pages:spec});
    await setCurrent(j.pdf,"extraido.pdf"); status("Páginas extraídas ✔ (quedó abierto el PDF extraído)"); }
  else { const j=await call("/api/delete_pages",{pdf:cur,pages:spec});
    await setCurrent(j.pdf,curName); status("Páginas borradas ✔"); }
});
$("bRotR").onclick=()=>run(async()=>{ await need(); const j=await call("/api/rotate",{pdf:cur,pages:"",degrees:90});
  await setCurrent(j.pdf,curName); status("Documento girado +90° ✔"); });
$("bRotL").onclick=()=>run(async()=>{ await need(); const j=await call("/api/rotate",{pdf:cur,pages:"",degrees:-90});
  await setCurrent(j.pdf,curName); status("Documento girado −90° ✔"); });
let mgItems=[]; let mgDragI=-1;
function mgBtn(t,fn){ const b=document.createElement("button"); b.textContent=t; b.className="mgbtn"; b.onclick=fn; return b; }
function renderMg(){ const box=$("mgList"); box.innerHTML="";
  if(!mgItems.length){ box.innerHTML="<div style='color:var(--mut);font-size:13.5px'>Aún no añades archivos. Pulsa «Añadir archivos…» y elige los PDF.</div>"; return; }
  mgItems.forEach((it,i)=>{ const d=document.createElement("div"); d.className="mgcard"; d.draggable=true; d.title="Arrástrame para cambiar el orden";
    const grip=document.createElement("span"); grip.textContent="⠿"; grip.style.cssText="color:var(--mut);cursor:grab;font-size:15px;flex:none";
    const num=document.createElement("span"); num.className="mgnum"; num.textContent=i+1;
    const nm=document.createElement("span"); nm.className="mgname"; nm.textContent=it.name; nm.title=it.name;
    const pg=document.createElement("span"); pg.className="mgpg"; pg.textContent=it.pages+" pág.";
    d.append(grip,num,nm,pg, mgBtn("✖",()=>{ mgItems.splice(i,1); renderMg(); }));
    d.addEventListener("dragstart",e=>{ mgDragI=i; d.classList.add("drag"); e.dataTransfer.effectAllowed="move"; try{e.dataTransfer.setData("text/plain",String(i));}catch(_){ } });
    d.addEventListener("dragend",()=>{ mgDragI=-1; box.querySelectorAll(".mgcard").forEach(c=>c.classList.remove("drag","over")); });
    d.addEventListener("dragover",e=>{ if(mgDragI<0||mgDragI===i)return; e.preventDefault(); e.dataTransfer.dropEffect="move"; d.classList.add("over"); });
    d.addEventListener("dragleave",()=>d.classList.remove("over"));
    d.addEventListener("drop",e=>{ e.preventDefault(); if(mgDragI<0||mgDragI===i)return; const mv=mgItems.splice(mgDragI,1)[0]; mgItems.splice(i,0,mv); mgDragI=-1; renderMg(); });
    box.appendChild(d); }); }
$("bMerge").onclick=()=>{ mgItems=[]; renderMg(); $("mgPosWrap").style.display=cur?"block":"none"; $("mgDlg").style.display="flex"; };
$("mgCancel").onclick=()=>{ $("mgDlg").style.display="none"; };
$("mgFiles").addEventListener("change",async e=>{ for(const f of e.target.files){
    const b64=await readB64(f); let pg="?";
    try{ const inf=await call("/api/info",{pdf:b64}); pg=inf.pages; }catch(_){ }
    mgItems.push({name:f.name,b64,pages:pg}); }
  e.target.value=""; renderMg(); });
$("mgOk").onclick=()=>run(async()=>{ if(!mgItems.length)throw new Error("Añade al menos un PDF");
  const files=mgItems.map(x=>x.b64); let arr, nota="";
  if(cur){ const pos=document.querySelector('input[name="mgPos"]:checked').value;
    arr=pos==="end"?[cur,...files]:[...files,cur]; nota=pos==="end"?"al final":"al principio"; }
  else arr=files;
  $("mgDlg").style.display="none";
  const j=await call("/api/merge",{pdfs:arr});
  await setCurrent(j.pdf, cur?curName:"unido.pdf");
  status("PDFs unidos ✔"+(cur?" ("+nota+" del documento que tenías)":"")+" — "+j.pages+" páginas en total"); });
$("bWord").onclick=()=>run(async()=>{ await need(); const j=await call("/api/to_word",{pdf:cur});
  saveB64(j.file,"convertido.docx","application/vnd.openxmlformats-officedocument.wordprocessingml.document"); status("Word creado ✔ (formato aproximado, revísalo)"); });
$("bExcel").onclick=()=>run(async()=>{ await need(); const j=await call("/api/to_excel",{pdf:cur});
  saveB64(j.file,"convertido.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"); status("Excel creado ✔ ("+j.tables+" tabla(s) detectada(s))"); });
$("bToPng").onclick=()=>run(async()=>{ await need(); const j=await call("/api/to_images",{pdf:cur});
  saveB64(j.zip,"paginas_png.zip","application/zip"); status("Imágenes PNG listas ✔"); });
$("bToTxt").onclick=()=>run(async()=>{ await need(); const j=await call("/api/to_text",{pdf:cur});
  $("txtOut").value=j.text; status("Texto extraído ✔ ("+j.pages+" páginas)"); });
$("bOcrTxt").onclick=()=>run(async()=>{ await need(); status("OCR en curso… puede tardar por página");
  const j=await call("/api/ocr_text",{pdf:cur,pages:""}); $("txtOut").value=j.text; status("OCR terminado ✔ ("+j.pages+" página(s))"); });
$("bOcrPdf").onclick=()=>run(async()=>{ await need(); status("OCR en curso… puede tardar por página");
  const j=await call("/api/ocr_pdf",{pdf:cur}); await setCurrent(j.pdf,"buscable_ocr.pdf"); status("PDF buscable creado ✔"); });
let markMode=false, stampPt=null;
function clearStampMark(){ const m=$("stampMark"); if(m)m.remove(); }
function drawStampMark(){ clearStampMark(); if(!stampPt)return;
  const im=document.querySelector(`.cpage[data-i="${stampPt.page}"]`); if(!im)return;
  const m=document.createElement("div"); m.id="stampMark"; m.textContent="📍"; m.title="Arrástrame para mover la marca";
  m.style.left=(im.offsetLeft+stampPt.fx*im.offsetWidth)+"px";
  m.style.top=(im.offsetTop+stampPt.fy*im.offsetHeight)+"px";
  $("pagesBox").appendChild(m);
  m.addEventListener("pointerdown",ev=>{ ev.preventDefault(); try{m.setPointerCapture(ev.pointerId);}catch(_){ }
    const move=e2=>{ const r=im.getBoundingClientRect();
      stampPt.fx=Math.max(0,Math.min(1,(e2.clientX-r.left)/r.width));
      stampPt.fy=Math.max(0,Math.min(1,(e2.clientY-r.top)/r.height));
      m.style.left=(im.offsetLeft+stampPt.fx*im.offsetWidth)+"px";
      m.style.top=(im.offsetTop+stampPt.fy*im.offsetHeight)+"px"; };
    const up=()=>{ m.removeEventListener("pointermove",move); m.removeEventListener("pointerup",up); };
    m.addEventListener("pointermove",move); m.addEventListener("pointerup",up); }); }
function setStampMark(ev,im){ const r=im.getBoundingClientRect();
  stampPt={page:+im.dataset.i, fx:(ev.clientX-r.left)/r.width, fy:(ev.clientY-r.top)/r.height};
  $("notePos").value="marca"; drawStampMark();
  status("Marca puesta 📍 El texto se estampará ahí; puedes arrastrar la flecha para ajustarla."); }
$("bMark").onclick=async()=>{ try{ await need(); }catch(e){ return; }
  markMode=!markMode; $("bMark").classList.toggle("activo",markMode);
  document.querySelectorAll(".cpage").forEach(im=>im.style.cursor=markMode?"crosshair":"");
  status(markMode?"Modo marcar ACTIVADO: haz clic en la página donde quieres el texto.":"Modo marcar desactivado."); };
const NOTE_POS={centro:[50,52,"c"],supcentro:[50,9,"c"],supizq:[7,9,"l"],supder:[93,9,"r"],infcentro:[50,94,"c"],infizq:[7,94,"l"],infder:[93,94,"r"]};
$("bNote").onclick=()=>run(async()=>{ await need(); const t=$("noteText").value; if(!t)throw new Error("Escribe el texto");
  const scope=$("noteScope").value, pos=$("notePos").value;
  let x,y,al,pg=page;
  if(pos==="marca"){ if(!stampPt)throw new Error("Primero pulsa «📍 Marcar posición» y haz clic sobre la página");
    x=stampPt.fx*100; y=stampPt.fy*100; al="l"; pg=stampPt.page; }
  else { [x,y,al]=NOTE_POS[pos]; }
  const j=await call("/api/add_text",{pdf:cur,page:pg,text:t,x_pct:x,y_pct:y,align:al,all:scope==="all"});
  await setCurrent(j.pdf,curName,true);
  status("Texto estampado ✔ ("+(scope==="all"?"en todas las páginas":"en esta página")+")"); });
$("bWm").onclick=()=>run(async()=>{ await need(); const j=await call("/api/watermark",{pdf:cur,text:$("wmText").value||"Aven PDF"});
  await setCurrent(j.pdf,"con_marca.pdf"); status("Marca de agua aplicada ✔"); });
$("wmImg").addEventListener("change",async e=>{ const f=e.target.files[0]; e.target.value=""; if(!f)return;
  run(async()=>{ await need(); const b64=await readB64(f);
    const j=await call("/api/watermark_image",{pdf:cur,image:b64,opacity:0.25});
    await setCurrent(j.pdf,"con_marca.pdf"); status("Imagen aplicada como marca de agua en todas las páginas ✔"); }); });
$("bRepl").onclick=()=>run(async()=>{ await need(); const o=$("findTxt").value; if(!o)throw new Error("Escribe el texto a buscar");
  const j=await call("/api/replace_text",{pdf:cur,old:o,new:$("replTxt").value,pages:""});
  if(!j.replaced){ status("No encontré ese texto en el PDF.",false); return; }
  await setCurrent(j.pdf,"editado.pdf"); status("Texto reemplazado en "+j.replaced+" lugar(es) ✔"); });
$("bEnc").onclick=()=>run(async()=>{ await need(); const p=$("newPw").value; if(!p)throw new Error("Escribe la contraseña nueva");
  const j=await call("/api/encrypt",{pdf:cur,password:p}); await setCurrent(j.pdf,"protegido.pdf"); status("PDF protegido con AES-256 ✔"); });
$("bDec").onclick=()=>run(async()=>{ await need(); const j=await call("/api/decrypt",{pdf:cur,password:$("pw").value});
  await setCurrent(j.pdf,"sin_clave.pdf"); status("Contraseña retirada ✔"); });
$("bComp").onclick=()=>run(async()=>{ await need(); const j=await call("/api/compress",{pdf:cur});
  await setCurrent(j.pdf,"optimizado.pdf"); status(`Comprimido: ${j.before_kb} KB → ${j.after_kb} KB ✔`); });
$("bStamp").onclick=()=>run(async()=>{ await need(); const n=$("signName").value; if(!n)throw new Error("Escribe tu nombre");
  const j=await call("/api/stamp",{pdf:cur,page,name:n}); await setCurrent(j.pdf,curName); status("Sello de firma estampado ✔"); });
$("bCert").onclick=()=>run(async()=>{ const n=$("certName").value, p=$("certPw").value;
  if(!n||!p)throw new Error("Escribe tu nombre y una contraseña para el certificado");
  const j=await call("/api/make_cert",{name:n,password:p});
  saveB64(j.file,"mi_certificado_avenpdf.pfx","application/x-pkcs12");
  status("Certificado creado ✔ Guárdalo bien: es tu identidad para firmar."); });
$("bSign").onclick=()=>run(async()=>{ await need(); const f=$("pfxFile").files[0]; if(!f)throw new Error("Elige tu archivo .pfx");
  const pfx=await readB64(f); const j=await call("/api/sign",{pdf:cur,pfx,password:$("pfxPw").value});
  await setCurrent(j.pdf,"firmado.pdf"); status("PDF firmado digitalmente ✔ (verifícalo en el panel de firmas de Nitro/Acrobat)"); });
$("bFields").onclick=()=>run(async()=>{ await need(); const j=await call("/api/form_fields",{pdf:cur});
  const box=$("fieldsBox"); box.innerHTML="";
  if(!j.fields.length){ box.textContent="Este PDF no tiene campos de formulario."; return; }
  j.fields.forEach(f=>{ const lab=document.createElement("label"); lab.textContent=f.name;
    const inp=document.createElement("input"); inp.type="text"; inp.value=f.value||""; inp.dataset.name=f.name; inp.className="ff";
    box.appendChild(lab); box.appendChild(inp); box.appendChild(document.createElement("br")); });
  const b=document.createElement("button"); b.className="bigbtn"; b.textContent="Guardar formulario rellenado";
  b.onclick=()=>run(async()=>{ const vals={}; document.querySelectorAll(".ff").forEach(i=>vals[i.dataset.name]=i.value);
    const j2=await call("/api/fill_form",{pdf:cur,values:vals}); await setCurrent(j2.pdf,"formulario.pdf"); status("Formulario guardado ✔"); });
  box.appendChild(b); status(j.fields.length+" campo(s) encontrado(s) ✔"); });
</script></body></html>
"""

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
            out = fn(d); code = 200
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
