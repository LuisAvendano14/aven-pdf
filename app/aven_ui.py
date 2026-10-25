# -*- coding: utf-8 -*-
"""Interfaz web de Aven PDF (HTML/CSS/JS). Archivo separado de aven_pdf.py
para que cada archivo quede bajo el limite de subida del conector de GitHub."""
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
.pgwrap{margin:0 auto 14px;background:#fff;box-shadow:0 4px 18px rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center;position:relative}
.pgwrap img.cpage{display:block;width:100%;height:100%;box-shadow:none}
.pgload{color:#94A3B8;font-size:13px}
.tph{width:110px;margin:0 auto;background:#fff;border:3px solid transparent;border-radius:4px;color:#94A3B8;display:flex;align-items:center;justify-content:center;font-size:15px;box-sizing:border-box}
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
main{display:grid;grid-template-columns:150px 1fr 250px;gap:0;flex:1;min-height:0;position:relative}
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
#thumbs::-webkit-scrollbar-thumb,#pageScroll::-webkit-scrollbar-thumb{background:#64748B;border-radius:6px;border:2px solid transparent;background-clip:content-box}
#thumbs::-webkit-scrollbar-thumb:hover,#pageScroll::-webkit-scrollbar-thumb:hover{background:#334155;border:2px solid transparent;background-clip:content-box}
#dropMsg h2{font-family:'Plus Jakarta Sans','Segoe UI',sans-serif}
.tabs button[data-t="inicio"].on{background:var(--acc);color:#fff}
#qpDel{color:#b91c1c}
#mgDlg,#svDlg,#pwDlg,#ciDlg,#xiDlg,#scDlg,#dkDlg,#cfDlg,#cpDlg{position:fixed;inset:0;background:rgba(10,18,35,.45);display:none;align-items:center;justify-content:center;z-index:50}
#mgDlg .box,#svDlg .box,#pwDlg .box,#ciDlg .box,#xiDlg .box,#scDlg .box,#dkDlg .box,#cfDlg .box,#cpDlg .box{background:#fff;border-radius:14px;padding:20px 24px;box-shadow:0 12px 40px rgba(0,0,0,.35);width:430px;max-width:94vw;text-align:left;max-height:88vh;overflow:auto}
#mgDlg button,#svDlg button,#pwDlg button,#ciDlg button,#xiDlg button,#scDlg button,#dkDlg button,#cfDlg button{padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:#f4f6fb;cursor:pointer;font-size:14px}
#mgDlg button:hover,#svDlg button:hover,#pwDlg button:hover,#ciDlg button:hover,#xiDlg button:hover,#scDlg button:hover,#dkDlg button:hover,#cfDlg button:hover{border-color:var(--acc)}
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
#sideTab{position:absolute;right:0;top:10px;z-index:45;background:#1E40AF;color:#fff;border:2px solid #fff;border-right:none;border-radius:12px 0 0 12px;padding:14px 9px;cursor:pointer;font-size:17px;font-weight:700;box-shadow:0 6px 18px rgba(15,23,42,.45)}
#sideTab:hover{background:#2563EB}
.mgcard{cursor:grab}
.mgcard.drag{opacity:.45}
.mgcard.over{outline:2px dashed var(--acc);outline-offset:-2px}
.mgthumb{width:40px;height:40px;object-fit:cover;border-radius:6px;flex:none}
#cfDlg .box{width:400px}
#splitBar{height:7px;cursor:ns-resize;background:linear-gradient(#e3e8f4,#ccd5ea);border-bottom:1px solid var(--line);flex:none}
#splitBar:hover{background:var(--acc)}
</style></head><body>
<div class="topbar"><div class="logo"><img id="logoImg" alt="Aven PDF" src="data:image/png;base64,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"></div><h1>Aven PDF <span class="ver">v1.7.3</span></h1>
<button id="bMenu" title="Oculta las opciones de arriba para ver el PDF mas grande">▲ Ocultar menú</button>
</div>
<div class="tabs" id="tabs">
<button data-t="inicio" class="on">📁 Archivo</button>
<button data-t="crear">✨ Crear</button>
<button data-t="paginas">📄 Páginas</button>
<button data-t="convertir">🔄 Convertir</button>
<button data-t="editar">✏️ Editar</button>
<button data-t="proteger">🔒 Proteger</button>
<button data-t="formularios">🧾 Formularios</button>
</div>
<div class="ribbon on" id="tab-inicio">
  <div class="grp"><div class="rowbtns">
    <label class="bigbtn" id="bOpenLbl"><span class="ic">📂</span>Abrir PDF<input type="file" id="file" accept="application/pdf" hidden></label>
    <button class="bigbtn" id="bDownload" disabled><span class="ic"><svg width="26" height="26" viewBox="0 0 24 24"><path fill="#1E40AF" d="M11 2.5h2V9h3.4L12 14.6 7.6 9H11z"/><path fill="#1E40AF" d="M4.5 15.4v2.9c0 1 .8 1.8 1.8 1.8h11.4c1 0 1.8-.8 1.8-1.8v-2.9h-2.7v2.7H7.2v-2.7z"/></svg></span>Descargar PDF</button>
    <button class="bigbtn" id="bSave" disabled><span class="ic">💾</span>Guardar cambios</button>
    <button class="bigbtn" id="bClose" disabled><span class="ic">✖</span>Cerrar documento</button>
  </div></div>
  <div class="grp"><label>Contraseña del PDF (si tiene)</label>
    <input type="password" id="pw" placeholder="••••••">
    <button class="bigbtn" id="bPwSet"><span class="ic">🔒</span>Adherir al PDF</button>
  </div>
</div>
<div class="ribbon" id="tab-crear">
  <div class="grp"><button class="bigbtn" id="bImgPdf"><span class="ic">🖼️</span>Imágenes a PDF</button>
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
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bComp"><span class="ic">🗜️</span>Comprimir</button>
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bDeskew"><span class="ic">📐</span>Enderezar</button>
  </div></div>
</div>
<div class="ribbon" id="tab-convertir">
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bWord"><span class="ic"><svg width="27" height="27" viewBox="0 0 24 24"><path d="M6 2h8l4 4v16H6z" fill="#185ABD"/><path d="M14 2l4 4h-4z" fill="#7FB2F0"/><text x="11.8" y="18.6" font-size="10.5" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="Arial, sans-serif">W</text></svg></span>a Word</button>
    <button class="bigbtn" id="bExcel"><span class="ic"><svg width="27" height="27" viewBox="0 0 24 24"><path d="M6 2h8l4 4v16H6z" fill="#107C41"/><path d="M14 2l4 4h-4z" fill="#9AD8B5"/><path d="M8.6 13.2h9.2M8.6 17h9.2M13.2 10.4v9.4" stroke="#ffffff" stroke-width="0.8" opacity="0.5"/><text x="11.4" y="10.6" font-size="8.6" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="Arial, sans-serif">X</text></svg></span>a Excel</button>
    <button class="bigbtn" id="bToPng"><span class="ic">🖼️</span>a imágenes PNG</button>
    <button class="bigbtn" id="bExtImg"><span class="ic">🎞️</span>Extraer imágenes</button>
    <button class="bigbtn" id="bToTxt"><span class="ic">🔤</span>a texto</button>
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bOcrTxt"><span class="ic">👁️</span>OCR: leer escaneado</button>
    <button class="bigbtn" id="bOcrPdf"><span class="ic">🔎</span>OCR: PDF buscable</button>
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bScan"><span class="ic">🖨️</span>PDF escaneado</button>
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
</div>
<div class="ribbon" id="tab-formularios">
  <div class="grp"><button class="bigbtn" id="bFields"><span class="ic">🧾</span>Ver campos</button>
  </div>
  <div class="grp wide"><div id="fieldsBox" style="font-size:13.5px">Aquí aparecen los campos si el PDF es un formulario.</div>
  </div>
</div>
<div id="splitBar" title="Arrastra hacia arriba o abajo: regula el espacio entre el menu y el PDF"></div>
<main>
<div id="thumbs"><div class="ptabs"><button id="ptPages" class="on">Páginas</button><button id="ptMarks">Marcadores</button></div><div id="thumbList"></div><div id="tocList" style="display:none;text-align:left;font-size:13px"></div></div>
<div id="viewer">
<div id="pagebar">
<div class="pb"><button id="zout">−</button><span style="font-size:13px">Zoom</span><button id="zin">+</button>
<button id="qpDl" title="Descargar el PDF actual con nombre de versión (…_AvenPDF_v01, v02…)"><svg width="14" height="14" viewBox="0 0 24 24" style="vertical-align:-2px"><path fill="currentColor" d="M11 2.5h2V9h3.4L12 14.6 7.6 9H11z"/><path fill="currentColor" d="M4.5 15.4v2.9c0 1 .8 1.8 1.8 1.8h11.4c1 0 1.8-.8 1.8-1.8v-2.9h-2.7v2.7H7.2v-2.7z"/></svg> Descargar</button>
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
<div id="cfDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:6px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">Aven PDF</div>
<div id="cfMsg" style="font-size:14px;line-height:1.55;white-space:pre-line"></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="cfOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Aceptar</button><button id="cfCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="ciDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🖼️ Imágenes a PDF</div>
<div style="font-size:13px;color:var(--mut)">Añade las imágenes y arrástralas para ordenarlas: el PDF se crea en ese orden exacto.</div>
<div id="ciList" style="margin-top:8px"></div>
<div style="margin-top:10px"><label class="bigbtn" style="display:inline-flex"><span class="ic">➕</span>Añadir imágenes…<input type="file" id="ciFiles" accept="image/*" multiple hidden></label></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="ciOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Crear PDF</button><button id="ciCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="xiDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🎞️ Extraer imágenes del PDF</div>
<div style="font-size:13px;color:var(--mut)">Saca las fotos e imágenes que el documento trae DENTRO. No es lo mismo que «a imágenes PNG», que fotografía las páginas completas.</div>
<div style="margin-top:10px;font-size:14px;display:flex;flex-direction:column;gap:8px">
<label style="cursor:pointer"><input type="radio" name="xiMode" value="all" checked> Todas las páginas</label>
<label style="cursor:pointer"><input type="radio" name="xiMode" value="range"> De la página <input type="number" id="xiFrom" value="1" min="1" style="width:64px;padding:5px 7px;border-radius:7px;border:1px solid var(--line)"> a la <input type="number" id="xiTo" value="1" min="1" style="width:64px;padding:5px 7px;border-radius:7px;border:1px solid var(--line)"> <span id="xiTotal" style="color:var(--mut)"></span></label>
<label style="cursor:pointer"><input type="radio" name="xiMode" value="list"> Páginas sueltas: <input type="text" id="xiList" placeholder="Ej. 2, 5, 7" style="width:130px;padding:5px 7px;border-radius:7px;border:1px solid var(--line)"></label>
</div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="xiOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Extraer imágenes</button><button id="xiCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="cpDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🗜️ Comprimir el PDF</div>
<div id="cpInfo" style="font-size:13px;color:var(--mut)">Comprimir achica las imágenes que trae el PDF (en un escaneo, casi todo el peso está ahí).</div>
<div style="margin-top:10px;font-size:14px;display:flex;flex-direction:column;gap:8px">
<label style="cursor:pointer"><input type="radio" name="cpLv" value="pantalla"> <b>Pantalla</b> — el más ligero: para ver en pantalla y compartir.</label>
<label style="cursor:pointer"><input type="radio" name="cpLv" value="media" checked> <b>Equilibrado</b> — buen tamaño y se sigue viendo bien al imprimir.</label>
<label style="cursor:pointer"><input type="radio" name="cpLv" value="alta"> <b>Alta calidad</b> — achica poco, casi sin pérdida visible.</label>
</div>
<div style="font-size:13px;color:var(--mut);margin-top:8px">En documentos grandes puede tardar varios minutos.</div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="cpOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">🗜️ Comprimir</button><button id="cpCancel">Cancelar</button></div>
</div></div>
<div id="scDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🖨️ Convertir a PDF escaneado</div>
<div style="font-size:13px;color:var(--mut)">El documento quedará como si lo hubieras escaneado en papel: imagen por página, con su leve inclinación y textura. Ya no se podrá seleccionar el texto.</div>
<div style="margin-top:10px;font-size:14px;display:flex;flex-direction:column;gap:8px">
<label style="cursor:pointer"><input type="radio" name="scMode" value="color" checked> A color</label>
<label style="cursor:pointer"><input type="radio" name="scMode" value="bw"> Blanco y negro</label>
</div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="scOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Crear PDF escaneado</button><button id="scCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="dkDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">📐 Enderezar PDF</div>
<div style="font-size:13px;color:var(--mut)">Detecta las páginas escaneadas chuecas y las endereza. El resultado queda en imagen, como en las webs de enderezado.</div>
<div style="margin-top:10px;font-size:14px;display:flex;flex-direction:column;gap:8px">
<label style="cursor:pointer"><input type="radio" name="dkMode" value="auto" checked> Automático: revisar todo y corregir solo las chuecas</label>
<label style="cursor:pointer"><input type="radio" name="dkMode" value="range"> De la página <input type="number" id="dkFrom" value="1" min="1" style="width:64px;padding:5px 7px;border-radius:7px;border:1px solid var(--line)"> a la <input type="number" id="dkTo" value="1" min="1" style="width:64px;padding:5px 7px;border-radius:7px;border:1px solid var(--line)"> <span id="dkTotal" style="color:var(--mut)"></span></label>
<label style="cursor:pointer"><input type="radio" name="dkMode" value="list"> Páginas sueltas: <input type="text" id="dkList" placeholder="Ej. 2, 5, 7" style="width:130px;padding:5px 7px;border-radius:7px;border:1px solid var(--line)"></label>
</div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="dkOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Enderezar</button><button id="dkCancel" style="flex:1">Cancelar</button></div>
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
let curDocId=null, pageSizes=[]; const docIds=new Map();
let pgObs=null, thObs=null, loadQ=[], loadActive=0;
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
  if(payload && payload.pdf && payload.pdf===cur && curDocId){ payload=Object.assign({},payload,{doc_id:curDocId}); delete payload.pdf; }
  const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const j=await r.json(); if(!r.ok||j.error) throw new Error(j.error||("HTTP "+r.status));
  if(j && j.doc_id && j.pdf){ docIds.set(j.pdf,j.doc_id); if(docIds.size>30)docIds.delete(docIds.keys().next().value); }
  return j;
}
function b64ToBlob(b64,mime="application/pdf"){
  const bin=atob(b64),arr=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);
  return new Blob([arr],{type:mime});
}
let dlNote="";
function saveB64(b64,name,mime="application/pdf"){
  const a=document.createElement("a");a.href=URL.createObjectURL(b64ToBlob(b64,mime));a.download=name;a.className="dl";a.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" style="vertical-align:-2px"><path fill="#ffffff" d="M11 2.5h2V9h3.4L12 14.6 7.6 9H11z"/><path fill="#ffffff" d="M4.5 15.4v2.9c0 1 .8 1.8 1.8 1.8h11.4c1 0 1.8-.8 1.8-1.8v-2.9h-2.7v2.7H7.2v-2.7z"/></svg> Descargar';
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
  cur=b64; if(name)curName=name;
  curDocId=docIds.get(b64)||null;
  let info;
  if(curDocId) info=await call("/api/info",{doc_id:curDocId,password:$("pw").value});
  else{ info=await call("/api/open",{pdf:cur,password:$("pw").value}); if(info.doc_id){ curDocId=info.doc_id; docIds.set(b64,curDocId); } }
  pages=info.pages; pageSizes=info.page_sizes||[];
  page=stayPage?prevPage:0;
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
  if(pgObs)pgObs.disconnect(); loadQ=[];
  pgObs=new IntersectionObserver(es=>{ es.forEach(en=>{ if(en.isIntersecting) queueLoad(en.target); }); },{root:$("pageScroll"),rootMargin:"700px 0px"});
  for(let i=0;i<pages;i++){
    const sz=pageSizes[i]||pageSizes[0]||[595,842];
    const wrap=document.createElement("div"); wrap.className="pgwrap"; wrap.dataset.pg=i;
    wrap.style.width=Math.round(sz[0]*zoom)+"px"; wrap.style.height=Math.round(sz[1]*zoom)+"px";
    const ph=document.createElement("div"); ph.className="pgload"; ph.textContent="Página "+(i+1); wrap.appendChild(ph);
    wrap.onclick=()=>{ page=i; syncLabel(); };
    box.appendChild(wrap); pgObs.observe(wrap);
  }
  if(stampPt) drawStampMark();
  syncLabel();
  requestAnimationFrame(()=>gotoPage(page,false));
}
function queueLoad(wrap){ if(wrap.dataset.done||wrap.dataset.queued)return; wrap.dataset.queued="1"; loadQ.push(wrap); pumpQ(); }
function pumpQ(){ while(loadActive<4&&loadQ.length){ const w=loadQ.shift(); loadActive++; loadPageImg(w).finally(()=>{ loadActive--; pumpQ(); }); } }
async function loadPageImg(wrap){
  const i=+wrap.dataset.pg, gen=renderGen;
  try{
    const j=await call("/api/render",{doc_id:curDocId,page:i,zoom,password:$("pw").value});
    if(gen!==renderGen)return;
    if(i===0)lastPix={w:j.w,h:j.h,zoom};
    const im=document.createElement("img"); im.className="cpage"; im.src="data:image/png;base64,"+j.png; im.dataset.i=i;
    im.onclick=(ev)=>{ page=i; syncLabel(); if(editMode) pickLine(ev,im,i); else if(markMode) setStampMark(ev,im); };
    if(editMode) im.style.cursor="text";
    wrap.innerHTML=""; wrap.appendChild(im); wrap.dataset.done="1";
    if(stampPt&&stampPt.page===i) drawStampMark();
  }catch(e){ wrap.innerHTML=""; const d=document.createElement("div"); d.className="pgload"; d.textContent="No se pudo cargar la página "+(i+1); wrap.appendChild(d); }
}
function syncThumbs(){ document.querySelectorAll("#thumbList .titem").forEach((w,k)=>{ const im=w.querySelector("img"); if(im)im.classList.toggle("sel",k===page); }); }
function syncLabel(){
  $("pgLabel").textContent=pages?`Página ${page+1} de ${pages}`:"—";
  document.querySelectorAll(".pgwrap").forEach(im=>{ im.style.outline=(+im.dataset.pg===page)?"3px solid var(--acc)":"none"; });
  syncThumbs();
}
function gotoPage(i,smooth=true){
  if(!pages)return; page=Math.max(0,Math.min(pages-1,i));
  const el=document.querySelector(`.pgwrap[data-pg="${page}"]`)||document.querySelector(`.cpage[data-i="${page}"]`);
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
      document.querySelectorAll(".pgwrap").forEach(im=>{ if(im.getBoundingClientRect().top<=top) curI=+im.dataset.pg; });
      if(curI!==page){ page=curI; syncLabel(); }
    });
  });
}
let thumbGen=0;
function renumberThumbs(){ document.querySelectorAll("#thumbList .titem").forEach((w,k)=>{ w.dataset.idx=k; const n=w.querySelector(".tnum"); if(n)n.textContent=k+1; }); }
async function buildThumbs(){
  const gen=++thumbGen;
  const box=$("thumbList"); box.innerHTML="";
  if(thObs)thObs.disconnect();
  thObs=new IntersectionObserver(es=>{ es.forEach(en=>{ if(en.isIntersecting) loadThumb(en.target); }); },{root:$("thumbs"),rootMargin:"500px 0px"});
  for(let i=0;i<pages;i++){
    const s=pageSizes[i]||pageSizes[0]||[595,842]; const h=Math.round(110*s[1]/Math.max(1,s[0]));
    const wrap=document.createElement("div"); wrap.className="titem"; wrap.draggable=true; wrap.dataset.idx=i;
    const ph=document.createElement("div"); ph.className="tph"; ph.style.height=h+"px"; ph.textContent="…";
    const num=document.createElement("div"); num.className="tnum"; num.textContent=(i+1);
    wrap.appendChild(ph); wrap.appendChild(num); box.appendChild(wrap); wrap._ph=ph;
    ph.onclick=()=>{ const idx=[...box.querySelectorAll(".titem")].indexOf(wrap); if(idx>=0)gotoPage(idx); };
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
        await setCurrent(j.pdf,curName,true); page=to; gotoPage(to,false); syncLabel();
        status(`Página movida a la posición ${to+1} ✔ (arrastra las miniaturas para reordenar)`); });
    });
    thObs.observe(wrap);
  }
  renumberThumbs(); syncThumbs();
  attachScrollSync();
}
async function loadThumb(wrap){
  if(wrap.dataset.done)return; wrap.dataset.done="1";
  const i=+wrap.dataset.idx, gen=thumbGen;
  try{
    const j=await call("/api/render",{doc_id:curDocId,page:i,zoom:0.22,password:$("pw").value});
    if(gen!==thumbGen)return;
    const im=document.createElement("img"); im.src="data:image/png;base64,"+j.png;
    im.onclick=()=>{ const idx=[...$("thumbList").querySelectorAll(".titem")].indexOf(wrap); if(idx>=0)gotoPage(idx); };
    if(wrap._ph) wrap._ph.replaceWith(im);
  }catch(e){ }
}
async function need(){ if(!cur){status("Primero abre un PDF (pestaña Inicio).",false); gotoTab("inicio"); throw new Error("sin archivo");} }
async function run(fn,msg){ try{ clearDownloads(); status("Procesando…"); await fn(); if(msg)status(msg);}catch(e){ status("Error: "+e.message,false);} }
function wipeViewer(msg){
  renderGen++; thumbGen++; if(pgObs)pgObs.disconnect(); if(thObs)thObs.disconnect(); loadQ=[];
  $("pagesBox").innerHTML=""; $("thumbList").innerHTML=""; $("tocList").innerHTML="";
  $("pgLabel").textContent="—"; $("emptyMsg").style.display="block"; status(msg||"Listo.");
}
$("file").addEventListener("change",async e=>{ const f=e.target.files[0]; if(!f)return;
  if(!await confirmarReemplazo()){ e.target.value=""; return; }
  fileHandle=null; wipeViewer("Cargando "+f.name+"…");
  run(async()=>{ await setCurrent(await readB64(f), f.name); dirty=false; dlVer=0; status("PDF cargado ✔ (el anterior se cerró)"); }); });
document.getElementById('bOpenLbl').addEventListener("click",async e=>{
  if(!window.showOpenFilePicker) return;
  e.preventDefault();
  if(!await confirmarReemplazo()) return;
  try{
    const [h]=await window.showOpenFilePicker({types:[{description:"PDF",accept:{"application/pdf":[".pdf"]}}],multiple:false});
    const f=await h.getFile(); fileHandle=h;
    wipeViewer("Cargando "+f.name+"…");
    run(async()=>{ await setCurrent(await readB64(f), f.name); dirty=false; dlVer=0; status("PDF cargado ✔ (con Guardar podrás reemplazar el original)"); });
  }catch(err){ }
});
$("bClose").onclick=async()=>{ if(cur && !await askConfirm("¿Cerrar el documento? Los cambios que no hayas descargado se perderán."))return; cur=null; curDocId=null; pages=0; page=0; lastToc=[];
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
  confirmarReemplazo().then(ok=>{ if(ok) run(async()=>{ await setCurrent(await readB64(f), f.name); dirty=false; dlVer=0; status("PDF cargado ✔"); }); }); });
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
(function(){ const bar=$("splitBar"); if(!bar)return; let drag=false;
  bar.addEventListener("pointerdown",e=>{ drag=true; try{bar.setPointerCapture(e.pointerId);}catch(_){ } e.preventDefault(); });
  bar.addEventListener("pointermove",e=>{ if(!drag)return; const r=document.querySelector(".ribbon.on"); if(!r)return;
    let h=e.clientY-r.getBoundingClientRect().top; h=Math.max(38,Math.min(360,h));
    document.querySelectorAll(".ribbon").forEach(x=>{ x.style.height=h+"px"; x.style.overflowY="auto"; }); });
  bar.addEventListener("pointerup",()=>{ drag=false; });
  bar.addEventListener("pointercancel",()=>{ drag=false; });
})();
let cfRes=null;
function askConfirm(msg){ return new Promise(res=>{ cfRes=res; $("cfMsg").textContent=msg;
  $("cfOk").textContent="Aceptar"; $("cfCancel").style.display=""; $("cfDlg").style.display="flex"; }); }
function askInfo(msg){ return new Promise(res=>{ cfRes=res; $("cfMsg").textContent=msg;
  $("cfOk").textContent="Entendido"; $("cfCancel").style.display="none"; $("cfDlg").style.display="flex"; }); }
$("cfOk").onclick=()=>{ $("cfDlg").style.display="none"; if(cfRes)cfRes(true); cfRes=null; };
$("cfCancel").onclick=()=>{ $("cfDlg").style.display="none"; if(cfRes)cfRes(false); cfRes=null; };
async function confirmarReemplazo(){
  if(!cur) return true;
  return askConfirm("Ya hay un documento abierto ("+curName+").\n\nSi continúas, ese documento se cerrará y perderás los cambios que NO hayas descargado.\n\n¿Cerrar el actual y continuar?");
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
  await setCurrent(j.pdf,curName,true); $("pwDlg").style.display="flex"; });
$("pwOkBtn").onclick=()=>{ $("pwDlg").style.display="none"; status("Contraseña adherida ✔ El PDF la pedirá al abrirse."); };
let ciItems=[], ciDragI=-1;
function renderCi(){ const box=$("ciList"); box.innerHTML="";
  if(!ciItems.length){ box.innerHTML="<div style='color:var(--mut);font-size:13.5px'>Aún no añades imágenes. Pulsa «Añadir imágenes…» y elige las fotos o escaneos.</div>"; return; }
  ciItems.forEach((it,i)=>{ const d=document.createElement("div"); d.className="mgcard"; d.draggable=true; d.title="Arrástrame para cambiar el orden";
    const grip=document.createElement("span"); grip.textContent="⠿"; grip.style.cssText="color:var(--mut);cursor:grab;font-size:15px;flex:none";
    const im=document.createElement("img"); im.src=it.url; im.className="mgthumb";
    const num=document.createElement("span"); num.className="mgnum"; num.textContent=i+1;
    const nm=document.createElement("span"); nm.className="mgname"; nm.textContent=it.name; nm.title=it.name;
    const pg=document.createElement("span"); pg.className="mgpg"; pg.textContent=Math.max(1,Math.round(it.size/1024))+" KB";
    d.append(grip,im,num,nm,pg, mgBtn("✖",()=>{ ciItems.splice(i,1); renderCi(); }));
    d.addEventListener("dragstart",e=>{ ciDragI=i; d.classList.add("drag"); e.dataTransfer.effectAllowed="move"; try{e.dataTransfer.setData("text/plain",String(i));}catch(_){ } });
    d.addEventListener("dragend",()=>{ ciDragI=-1; box.querySelectorAll(".mgcard").forEach(c=>c.classList.remove("drag","over")); });
    d.addEventListener("dragover",e=>{ if(ciDragI<0||ciDragI===i)return; e.preventDefault(); e.dataTransfer.dropEffect="move"; d.classList.add("over"); });
    d.addEventListener("dragleave",()=>d.classList.remove("over"));
    d.addEventListener("drop",e=>{ e.preventDefault(); if(ciDragI<0||ciDragI===i)return; const mv=ciItems.splice(ciDragI,1)[0]; ciItems.splice(i,0,mv); ciDragI=-1; renderCi(); });
    box.appendChild(d); }); }
$("bImgPdf").onclick=()=>run(async()=>{ if(!await confirmarReemplazo())return; ciItems=[]; renderCi(); $("ciDlg").style.display="flex"; });
$("ciCancel").onclick=()=>{ $("ciDlg").style.display="none"; };
$("ciFiles").addEventListener("change",async e=>{ for(const f of e.target.files){
    ciItems.push({name:f.name, b64:await readB64(f), url:URL.createObjectURL(f), size:f.size}); }
  e.target.value=""; renderCi(); });
$("ciOk").onclick=()=>run(async()=>{ if(!ciItems.length)throw new Error("Añade al menos una imagen");
  const arr=ciItems.map(x=>x.b64); $("ciDlg").style.display="none";
  const j=await call("/api/images_to_pdf",{images:arr}); await setCurrent(j.pdf,"desde_imagenes.pdf");
  status("PDF creado desde "+arr.length+" imagen(es) ✔"); });
$("bTxtPdf").onclick=()=>run(async()=>{ if(!await confirmarReemplazo())return; const t=$("txtBody").value; if(!t.trim())throw new Error("Escribe un texto");
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
    await setCurrent(j.pdf,curName,true); status("Páginas borradas ✔"); }
});
$("bRotR").onclick=()=>run(async()=>{ await need(); const j=await call("/api/rotate",{pdf:cur,pages:"",degrees:90});
  await setCurrent(j.pdf,curName,true); status("Documento girado +90° ✔"); });
$("bRotL").onclick=()=>run(async()=>{ await need(); const j=await call("/api/rotate",{pdf:cur,pages:"",degrees:-90});
  await setCurrent(j.pdf,curName,true); status("Documento girado −90° ✔"); });
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
  const j=await call("/api/ocr_pdf",{pdf:cur}); await setCurrent(j.pdf,"buscable_ocr.pdf",true); status("PDF buscable creado ✔"); });
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
  await setCurrent(j.pdf,"con_marca.pdf",true); status("Marca de agua aplicada ✔"); });
$("wmImg").addEventListener("change",async e=>{ const f=e.target.files[0]; e.target.value=""; if(!f)return;
  run(async()=>{ await need(); const b64=await readB64(f);
    const j=await call("/api/watermark_image",{pdf:cur,image:b64,opacity:0.25});
    await setCurrent(j.pdf,"con_marca.pdf",true); status("Imagen aplicada como marca de agua en todas las páginas ✔"); }); });
$("bRepl").onclick=()=>run(async()=>{ await need(); const o=$("findTxt").value; if(!o)throw new Error("Escribe el texto a buscar");
  const j=await call("/api/replace_text",{pdf:cur,old:o,new:$("replTxt").value,pages:""});
  if(!j.replaced){ status("No encontré ese texto en el PDF.",false); return; }
  await setCurrent(j.pdf,"editado.pdf",true); status("Texto reemplazado en "+j.replaced+" lugar(es) ✔"); });
$("bEnc").onclick=()=>run(async()=>{ await need(); const p=$("newPw").value; if(!p)throw new Error("Escribe la contraseña nueva");
  const j=await call("/api/encrypt",{pdf:cur,password:p}); await setCurrent(j.pdf,"protegido.pdf",true); status("PDF protegido con AES-256 ✔"); });
$("bDec").onclick=()=>run(async()=>{ await need(); const j=await call("/api/decrypt",{pdf:cur,password:$("pw").value});
  await setCurrent(j.pdf,"sin_clave.pdf",true); status("Contraseña retirada ✔"); });
$("bComp").onclick=()=>run(async()=>{ await need();
  $("cpInfo").textContent="Tamaño actual: "+Math.round(cur.length*0.75/1024).toLocaleString("es")+" KB. Comprimir achica las imágenes que trae el PDF (en un escaneo, casi todo el peso está ahí).";
  $("cpDlg").style.display="flex"; });
$("cpCancel").onclick=()=>$("cpDlg").style.display="none";
$("cpOk").onclick=()=>run(async()=>{ const lv=document.querySelector('input[name="cpLv"]:checked').value; $("cpDlg").style.display="none";
  const j=await call("/api/compress",{pdf:cur,password:pwd,level:lv}); await setCurrent(j.pdf,"optimizado.pdf",true);
  if(j.after_kb<j.before_kb){ const pct=Math.round(100*(1-j.after_kb/j.before_kb));
    status(`Comprimido de verdad: ${j.before_kb} KB → ${j.after_kb} KB (−${pct}%, ${j.images_done} imágenes reducidas) ✔ — Descargar o Guardar para conservarlo`); }
  else { status(`Comprimir: el tamaño apenas cambió (${j.before_kb} KB → ${j.after_kb} KB)`, false);
    askInfo("Con este nivel el tamaño no bajó ("+j.before_kb+" KB → "+j.after_kb+" KB; imágenes reducidas: "+j.images_done+"). Si el documento es de escaneos, prueba el nivel «Pantalla», que es el que más achica."); }
});
function specFromDlg(pre){ const mode=document.querySelector('input[name="'+pre+'Mode"]:checked').value;
  if(mode==="all"||mode==="auto") return "";
  if(mode==="range"){ const a=parseInt($(pre+"From").value||"1",10), b=parseInt($(pre+"To").value||"1",10);
    if(!(a>=1&&b>=a&&b<=pages))throw new Error("Rango no válido: debe ir del 1 al "+pages+" y «desde» no puede ser mayor que «hasta»");
    return a+"-"+b; }
  const v=$(pre+"List").value.trim(); if(!v)throw new Error("Escribe las páginas, p. ej. 2, 5, 7"); return v; }
$("bExtImg").onclick=()=>run(async()=>{ await need(); $("xiTo").value=pages; $("xiTotal").textContent="(el documento tiene "+pages+")"; $("xiDlg").style.display="flex"; });
$("xiCancel").onclick=()=>{ $("xiDlg").style.display="none"; };
$("xiOk").onclick=()=>run(async()=>{ const spec=specFromDlg("xi"); $("xiDlg").style.display="none";
  const j=await call("/api/extract_images",{pdf:cur,pages:spec,password:$("pw").value});
  if(!j.count){ askInfo("Se encontraron 0 imágenes incrustadas en las páginas elegidas.\n\nOjo: «Extraer imágenes» saca las fotos que el PDF trae dentro; si lo que quieres es cada página como foto, usa «a imágenes PNG»."); status("Sin imágenes incrustadas en esas páginas."); return; }
  dlNote="Se encontraron "+j.count+" imagen(es) dentro del documento (en "+j.pages+" página(s) revisada(s)).";
  saveB64(j.zip,"imagenes_extraidas.zip","application/zip");
  status("Imágenes extraídas ✔ "+j.count+" encontrada(s)"); });
$("bScan").onclick=()=>run(async()=>{ await need(); $("scDlg").style.display="flex"; });
$("scCancel").onclick=()=>{ $("scDlg").style.display="none"; };
$("scOk").onclick=()=>run(async()=>{ const mode=document.querySelector('input[name="scMode"]:checked').value;
  $("scDlg").style.display="none"; status("Convirtiendo a PDF escaneado… puede tardar por página");
  const j=await call("/api/to_scanned",{pdf:cur,mode,password:$("pw").value});
  await setCurrent(j.pdf,"escaneado.pdf",true); status("PDF escaneado creado ✔ ("+j.pages+" páginas, modo "+(mode==="bw"?"blanco y negro":"color")+")"); });
$("bDeskew").onclick=()=>run(async()=>{ await need(); $("dkTo").value=pages; $("dkTotal").textContent="(el documento tiene "+pages+")"; $("dkDlg").style.display="flex"; });
$("dkCancel").onclick=()=>{ $("dkDlg").style.display="none"; };
$("dkOk").onclick=()=>run(async()=>{ const spec=specFromDlg("dk"); $("dkDlg").style.display="none"; status("Enderezando… puede tardar por página");
  const j=await call("/api/deskew",{pdf:cur,pages:spec,password:$("pw").value});
  await setCurrent(j.pdf,"enderezado.pdf",true);
  status(j.fixed?("Enderezado ✔ "+j.fixed+" página(s) corregida(s)"):"Sin cambios: ninguna página estaba chueca ✔"); });
$("bFields").onclick=()=>run(async()=>{ await need(); const j=await call("/api/form_fields",{pdf:cur});
  const box=$("fieldsBox"); box.innerHTML="";
  if(!j.fields.length){ box.textContent="Este PDF no tiene campos de formulario."; return; }
  j.fields.forEach(f=>{ const lab=document.createElement("label"); lab.textContent=f.name;
    const inp=document.createElement("input"); inp.type="text"; inp.value=f.value||""; inp.dataset.name=f.name; inp.className="ff";
    box.appendChild(lab); box.appendChild(inp); box.appendChild(document.createElement("br")); });
  const b=document.createElement("button"); b.className="bigbtn"; b.textContent="Guardar formulario rellenado";
  b.onclick=()=>run(async()=>{ const vals={}; document.querySelectorAll(".ff").forEach(i=>vals[i.dataset.name]=i.value);
    const j2=await call("/api/fill_form",{pdf:cur,values:vals}); await setCurrent(j2.pdf,"formulario.pdf",true); status("Formulario guardado ✔"); });
  box.appendChild(b); status(j.fields.length+" campo(s) encontrado(s) ✔"); });
</script></body></html>
"""
