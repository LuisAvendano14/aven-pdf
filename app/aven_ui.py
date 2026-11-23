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
#pagesBox.editing .cpage{cursor:text}
#emptyPlus{width:96px;height:96px;border-radius:50%;border:3px dashed #94A3B8;background:#fff;color:#64748B;font-size:54px;line-height:1;cursor:pointer;transition:all .15s ease}
#emptyPlus:hover{border-color:var(--az);color:var(--az);transform:scale(1.05)}
.certpin{position:absolute;transform:translate(-50%,-50%);background:#7C3AED;color:#fff;border-radius:50%;width:20px;height:20px;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;pointer-events:none;box-shadow:0 1px 4px rgba(0,0,0,.45);z-index:3}
.certbadge{background:#7C3AED;color:#fff;border-radius:50%;width:20px;height:20px;font-size:12px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;flex:none}
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
.empty{color:var(--mut);font-size:16px;margin-top:70px;line-height:1.7;display:flex;flex-direction:column;align-items:center;gap:14px;text-align:center}
.wide{flex-basis:100%}
#bMenu{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.55);color:#fff;border-radius:8px;padding:6px 12px;cursor:pointer;font-size:13px;white-space:nowrap}
#bMenu:hover{background:rgba(255,255,255,.28)}
#pagesBox{position:relative}
#hlBox{position:absolute;border:2px solid var(--acc);background:rgba(232,134,46,.16);pointer-events:none;z-index:5;border-radius:2px}
#pagebar button.mini{padding:2px 7px;font-size:12px}
.qa:disabled{opacity:.45;cursor:default}
select{padding:6px 8px;border-radius:8px;border:1px solid var(--line);font-size:13px;background:#fff}
#editBar{display:none;align-items:center;gap:8px;background:#fff7ea;border-bottom:2px solid var(--acc);padding:8px 12px;font-size:13.5px}
#editBar input{flex:1;width:auto}
#editBar button{background:#fff;border:1px solid var(--line);border-radius:8px;padding:7px 13px;cursor:pointer;font-size:13.5px;font-weight:600}
#editBar button:hover{border-color:var(--acc)}
#editBar #editOk{background:var(--ok);color:#fff;border-color:var(--ok)}
#editBar{flex-wrap:wrap}
#editBar button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
#editBar input[type=color]{width:34px;height:30px;padding:1px;flex:none}
#editBar input[type=number]{flex:none}
#editBar select{max-width:155px;flex:none}
#editBar{position:absolute;z-index:40;box-shadow:0 10px 30px rgba(15,23,42,.35);border:1.5px solid var(--acc);border-radius:12px;max-width:94%}
#editBar>span{display:none}
#editBar #editInput{display:none}
#inlineInput{position:absolute;z-index:35;border:1.5px solid var(--acc);background:rgba(255,255,255,.98);outline:none;padding:0 3px;border-radius:3px;box-shadow:0 2px 8px rgba(15,23,42,.25)}
#imgBar{display:none;align-items:center;gap:8px;flex-wrap:wrap;background:#eef4ff;border-bottom:2px solid var(--az);padding:8px 12px;font-size:13px}
#imgBar button{background:#fff;border:1px solid var(--line);border-radius:8px;padding:6px 11px;cursor:pointer;font-size:13px;font-weight:600}
#imgBar #imOk{background:var(--ok);color:#fff;border-color:var(--ok)}
#imgBar label{display:flex;align-items:center;gap:4px;color:var(--mut)}
#pvDlg .pvb{background:#fff;border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer;font-size:13px;font-weight:600}
.bigbtn.activo{background:#FFE9D6;color:#7C2D12;border-color:var(--acc);box-shadow:0 0 0 2px var(--acc) inset}
.tabs button{font-family:'Plus Jakarta Sans','Segoe UI',sans-serif;font-weight:600}
.grp .cap{font-family:'Plus Jakarta Sans',sans-serif;font-weight:700}
input:focus,textarea:focus{border-color:var(--az);outline:2px solid rgba(30,64,175,.25);outline-offset:0}
#thumbs::-webkit-scrollbar,#pageScroll::-webkit-scrollbar{width:10px;height:10px}
#thumbs::-webkit-scrollbar-thumb,#pageScroll::-webkit-scrollbar-thumb{background:#64748B;border-radius:6px;border:2px solid transparent;background-clip:content-box}
#thumbs::-webkit-scrollbar-thumb:hover,#pageScroll::-webkit-scrollbar-thumb:hover{background:#334155;border:2px solid transparent;background-clip:content-box}
#dropMsg h2{font-family:'Plus Jakarta Sans','Segoe UI',sans-serif}
.tabs button[data-t="inicio"].on{background:var(--acc);color:#fff}
#qpDel{color:#b91c1c}
#pagebar{gap:10px;padding:8px 12px}
#pagebar button{display:inline-flex;align-items:center;gap:6px;font-weight:600;color:#1f2a44}
#pagebar button svg{flex:none}
#pagebar button:disabled{opacity:.45;cursor:default}
#pagebar .pbsep{width:1px;height:24px;background:#d7dde8;margin:0 2px;flex:none}
#pgLabel{font-weight:700;font-size:13.5px;color:#1f2a44;white-space:nowrap}
#zPct{font-size:12.5px;color:var(--mut);min-width:38px;text-align:center}
#zout,#zin{width:30px;justify-content:center;padding:6px 0}
.rowbtns{display:flex;gap:8px}
.rowbtns button{display:inline-flex;align-items:center;gap:7px;background:#fff;border:1px solid var(--line);border-radius:9px;padding:8px 14px;font-size:13.5px;font-weight:600;color:#1f2a44;cursor:pointer}
.rowbtns button:hover{border-color:var(--acc);color:var(--az)}
#mgDlg,#svDlg,#pwDlg,#ciDlg,#xiDlg,#scDlg,#dkDlg,#cfDlg,#cpDlg,#progDlg,#msgDlg,#openPwDlg,#txtDlg,#decDlg,#dlDlg,#pgDlg,#insDlg,#certDlg,#objDlg,#multiDlg,#openChoiceDlg,#poDlg,#rotDlg{position:fixed;inset:0;background:rgba(10,18,35,.45);display:none;align-items:center;justify-content:center;z-index:50}
#mgDlg .box,#svDlg .box,#pwDlg .box,#ciDlg .box,#xiDlg .box,#scDlg .box,#dkDlg .box,#cfDlg .box,#cpDlg .box,#progDlg .box,#msgDlg .box,#openPwDlg .box,#txtDlg .box,#decDlg .box,#dlDlg .box,#pgDlg .box,#insDlg .box,#certDlg .box,#objDlg .box,#multiDlg .box,#openChoiceDlg .box,#poDlg .box,#rotDlg .box{background:#fff;border-radius:14px;padding:20px 24px;box-shadow:0 12px 40px rgba(0,0,0,.35);width:430px;max-width:94vw;text-align:left;max-height:88vh;overflow:auto}
#mgDlg button,#svDlg button,#pwDlg button,#ciDlg button,#xiDlg button,#scDlg button,#dkDlg button,#cfDlg button,#cpDlg button,#progDlg button,#msgDlg button,#openPwDlg button,#txtDlg button,#decDlg button,#dlDlg button,#pgDlg button,#insDlg button,#certDlg button,#objDlg button,#multiDlg button,#openChoiceDlg button,#poDlg button,#rotDlg button{padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:#f4f6fb;cursor:pointer;font-size:14px}
#mgDlg button:hover,#svDlg button:hover,#pwDlg button:hover,#ciDlg button:hover,#xiDlg button:hover,#scDlg button:hover,#dkDlg button:hover,#cfDlg button:hover,#cpDlg button:hover,#progDlg button:hover,#msgDlg button:hover,#openPwDlg button:hover,#txtDlg button:hover,#decDlg button:hover,#dlDlg button:hover,#pgDlg button:hover,#insDlg button:hover,#certDlg button:hover,#objDlg button:hover,#multiDlg button:hover,#openChoiceDlg button:hover{border-color:var(--acc)}
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
#mgDlg .box.wide,#pgDlg .box.wide{width:min(1140px,97vw);height:min(93vh,940px);max-height:93vh;display:flex;flex-direction:column;overflow:hidden}
#mgDlg .box.wide #mgBoard{flex:1;min-height:0}
#pgDlg .box.wide #pgSecBoard{flex:1;min-height:0;display:flex;flex-direction:column}
#pgDlg .box.wide #pgBoard{flex:1;min-height:0;max-height:none !important}
.mggrid{display:grid;gap:9px;min-height:100%}
.mgcard{border-radius:11px;padding:8px 6px;cursor:grab;text-align:center;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:0;overflow:hidden}
.pggrid{display:grid;gap:8px;min-height:100%}
.pgchip{border:2px solid var(--line);border-radius:9px;padding:5px;text-align:center;cursor:pointer;background:#fff;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;min-height:0;overflow:hidden}
.boardScroll{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:2px 8px 8px 2px}
.boardScroll::-webkit-scrollbar,#pgBoard::-webkit-scrollbar{width:11px;height:11px}
.boardScroll::-webkit-scrollbar-thumb,#pgBoard::-webkit-scrollbar-thumb{background:#64748B;border-radius:6px;border:2px solid transparent;background-clip:content-box}
.boardScroll::-webkit-scrollbar-thumb:hover,#pgBoard::-webkit-scrollbar-thumb:hover{background:#334155;border:2px solid transparent;background-clip:content-box}
.boardScroll::-webkit-scrollbar-track,#pgBoard::-webkit-scrollbar-track{background:#eef1f7;border-radius:6px}
/* ===== 1.18: cinta en una sola banda y controles en una fila ===== */
.ribbon{flex-wrap:wrap;overflow:visible}
.ribbon input[type=text],.ribbon input[type=password]{width:168px}
.ribbon textarea{width:300px}
.grp{padding:0 8px}
.bigbtn{min-width:78px}
#pagebar{overflow-x:auto;overflow-y:hidden}
#pagebar .pb{flex-wrap:nowrap}
#pagebar button{padding:5px 8px;font-size:12.5px;white-space:nowrap}
#imgBar{flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden}
#imgBar>*{flex:none}
.minibtn{display:inline-flex;align-items:center;gap:5px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:5px 9px;font-size:12.5px;font-weight:600;color:#1f2a44;cursor:pointer}
.minibtn:hover{border-color:var(--acc);color:var(--az)}
#eraseRing{position:absolute;border:1.5px solid #7C2D12;background:rgba(124,45,18,.08);border-radius:50%;pointer-events:none;z-index:6;display:none;box-sizing:border-box}

#rbBar{display:none;background:#FEF3C7;border-bottom:2px solid #F59E0B;padding:8px 14px;gap:8px;align-items:center;flex-wrap:wrap;font-size:13px;color:#92400E}
#rbBar button{padding:6px 12px;border-radius:8px;border:1.5px solid #D97706;background:#fff;cursor:pointer;font-weight:600;color:#92400E}
#rbBar button:hover{background:#FFEDD5}
body.rbedit .ribbon button,body.rbedit .ribbon .bigbtn,body.rbedit #tabs button{outline:1.5px dashed #94A3B8;outline-offset:1px;cursor:grab}
body.rbedit .ribbon .grp{outline:1.5px dotted #CBD5E1;outline-offset:-1px}
.rbov{box-shadow:inset 0 0 0 3px #2563EB!important}
.rbdrag{opacity:.35}

.qa{flex:none}
.pb{flex-wrap:wrap}
.bigbtn{flex:none}
#tabs button{flex:none}
#pagebar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center}
.pb.c{flex-wrap:nowrap;justify-self:center}
.pb.r{grid-column:1/-1;justify-self:center;justify-content:center;margin-left:0;flex-wrap:wrap}
#rbBar button.on{background:var(--az);color:#fff;border-color:var(--az)}
.rbHandle{position:absolute;right:1px;bottom:1px;width:14px;height:14px;background:rgba(37,99,235,.4);border-radius:3px;cursor:nwse-resize;z-index:4}
#tipFloat{position:fixed;z-index:4000;max-width:330px;background:#1F2A44;color:#fff;font-size:12.5px;line-height:1.45;padding:8px 11px;border-radius:9px;box-shadow:0 8px 22px rgba(15,23,42,.35);display:none;pointer-events:none}

.titem.sel{outline:3px solid var(--az);outline-offset:-3px;background:#dbeafe}
</style></head><body>
<div class="topbar"><div class="logo"><img id="logoImg" alt="Aven PDF" src="data:image/png;base64,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"></div><h1>Aven PDF <span class="ver">v1.29</span><span id="winMode" style="font-size:11px;color:#64748B;font-weight:600;margin-left:8px"></span></h1>
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
<div id="rbBar"><span>🎨 <b>Modo editor:</b> arrastra las <b>pestañas</b> y los <b>botones</b> para cambiar su orden. Solo cambia la posición, no lo que hace cada botón. <b>Con ajuste</b>: se acomodan solos en los espacios. <b>Libre</b>: cada botón donde quieras y del tamaño que quieras.</span><span style="flex:1"></span><button id="rbModeSnap" class="on">🧲 Con ajuste</button><button id="rbModeFree">🆓 Libre</button><button id="rbSave">💾 Guardar</button><button id="rbReset">↩️ Restablecer original</button><button id="rbExit">✖ Salir sin guardar</button></div>
<div class="ribbon on" id="tab-inicio">
  <div class="grp"><div class="rowbtns">
    <label class="bigbtn" id="bOpenLbl"><span class="ic">📂</span>Abrir PDF<input type="file" id="file" accept="application/pdf" multiple hidden></label>
    <button class="bigbtn" id="bDownload" disabled><span class="ic"><svg width="26" height="26" viewBox="0 0 24 24"><path fill="#1E40AF" d="M11 2.5h2V9h3.4L12 14.6 7.6 9H11z"/><path fill="#1E40AF" d="M4.5 15.4v2.9c0 1 .8 1.8 1.8 1.8h11.4c1 0 1.8-.8 1.8-1.8v-2.9h-2.7v2.7H7.2v-2.7z"/></svg></span>Descargar PDF</button>
    <button class="bigbtn" id="bSave" disabled><span class="ic">💾</span>Guardar cambios</button>
    <button class="bigbtn" id="bClose" disabled><span class="ic">✖</span>Cerrar documento</button>
  </div></div>
</div>
<div class="ribbon" id="tab-crear">
  <div class="grp"><button class="bigbtn" id="bImgPdf"><span class="ic">🖼️</span>Imágenes a PDF</button>
  </div>
  <div class="grp"><div style="display:flex;gap:8px;align-items:stretch"><div style="display:flex;flex-direction:column;gap:4px"><input type="text" id="txtTitle" placeholder="Título del documento"><textarea id="txtBody" rows="2" placeholder="Escribe o pega el texto…"></textarea></div><button class="bigbtn" id="bTxtPdf"><span class="ic">📝</span>PDF desde texto</button></div>
  </div>
  <div class="grp"><button class="bigbtn" id="bCert"><span class="ic">🎓</span>Certificados en bloque</button>
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
    <button class="bigbtn" id="bOrder"><span class="ic">🗂️</span>Ordenar</button>
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
  </div></div>
  <div class="grp"><div class="rowbtns">
    <button class="bigbtn" id="bScan"><span class="ic">🖨️</span>PDF escaneado</button>
  </div></div>
  <div class="grp wide"><label>Texto resultante</label>
    <textarea id="txtOut" rows="4" style="width:100%" placeholder="Aquí aparece el texto extraído u OCR…" readonly></textarea>
    <div class="rowbtns" style="margin-top:6px"><button id="bTxtBig"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg> Ampliar texto</button><button id="bTxtClear"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.5 4.5l4 4L11 17H7.5L3.6 13.1a1.8 1.8 0 0 1 0-2.5l6.4-6.4a1.8 1.8 0 0 1 2.5 0z"/><path d="M8 21h13"/></svg> Limpiar</button></div>
  </div>
</div>
<div class="ribbon" id="tab-editar">
  <div class="grp"><button class="bigbtn" id="bRibbonEdit" data-tip="Ordenar la cinta: mueve las pestañas y los botones de lugar. Solo cambia la posición: cada botón sigue haciendo exactamente lo mismo."><span class="ic">🔀</span>Mover</button><span class="cap">Ordenar la cinta</span></div>
  <div class="grp"><div class="rowbtns"><button class="bigbtn" id="bEditMode"><span class="ic">✏️</span>Editar sobre el PDF</button><button class="bigbtn" id="bImgAdd"><span class="ic">🖼️</span>Insertar imagen</button></div>
    <input type="file" id="imgFile" accept="image/*" hidden>
  </div>
  <div class="grp"><div class="rowbtns"><button class="bigbtn" id="bToolPen"><span class="ic">✏️</span>Lápiz</button><button class="bigbtn" id="bToolHi"><span class="ic">🖍️</span>Resaltar</button><button class="bigbtn" id="bToolErase"><span class="ic">🧽</span>Borrador</button></div>
    <div class="rowbtns" style="align-items:center"><label style="font-size:12.5px">Color <input type="color" id="drawColor" value="#d32f2f"></label><label style="font-size:12.5px">Grosor <input type="range" id="drawWidth" min="1" max="12" value="3" style="width:84px"></label><button class="minibtn" id="bDrawApply">✔ Aplicar trazos</button><button class="minibtn" id="bDrawClear">🗑️ Limpiar</button></div>
  </div>
  <div class="grp"><input type="text" id="noteText" placeholder="Ej. REVISADO">
    <div class="rowbtns"><select id="noteScope" title="Alcance del estampado"><option value="page">En esta página</option><option value="all">En todas las páginas</option></select><select id="notePos" title="Ubicación del texto"><option value="centro">Centro</option><option value="supcentro">Arriba al centro</option><option value="supizq">Arriba a la izquierda</option><option value="supder">Arriba a la derecha</option><option value="infcentro">Abajo al centro</option><option value="infizq">Abajo a la izquierda</option><option value="infder">Abajo a la derecha</option></select><button class="minibtn" id="bNote">🏷️ Estampar texto</button></div>
  </div>
  <div class="grp"><input type="text" id="wmText" placeholder="Ej. CONFIDENCIAL">
    <div class="rowbtns"><button class="minibtn" id="bWm">💧 Marca de agua</button><label class="minibtn" title="Usa una imagen (un logo o un sello) como marca de agua en todas las páginas">🖼️ Imagen de marca<input type="file" id="wmImg" accept="image/*" hidden></label></div>
  </div>
  <div class="grp"><input type="text" id="findTxt" placeholder="Texto actual">
    <div class="rowbtns"><input type="text" id="replTxt" placeholder="Texto nuevo" style="width:150px"><button class="minibtn" id="bRepl">🔁 Buscar y reemplazar</button></div>
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
<div class="pb"><button id="zout" title="Alejar"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14"/></svg></button><span style="font-size:13px">Zoom</span><span id="zPct">140%</span><button id="zin" title="Acercar"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></button>
<span class="pbsep"></span>
<button id="qpDl" title="Descargar el PDF actual con nombre de versión (…_AvenPDF_v01, v02…)"><svg width="15" height="15" viewBox="0 0 24 24"><path fill="currentColor" d="M11 2.5h2V9h3.4L12 14.6 7.6 9H11z"/><path fill="currentColor" d="M4.5 15.4v2.9c0 1 .8 1.8 1.8 1.8h11.4c1 0 1.8-.8 1.8-1.8v-2.9h-2.7v2.7H7.2v-2.7z"/></svg> Descargar</button>
<button id="qpSave" title="Guardar cambios: reemplazar el archivo original o guardar una copia nueva"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3h11l5 5v13H5z"/><path d="M8 3v5h7V3"/><path d="M8 21v-7h8v7"/></svg> Guardar</button></div>
<div class="pb c"><button id="prev" title="Página anterior (flecha ←)"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 5.5L8 12l6.5 6.5"/></svg></button><span id="pgLabel">—</span><button id="next" title="Página siguiente (flecha →)"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 5.5L16 12l-6.5 6.5"/></svg></button></div>
<div class="pb r">
<button class="qa" id="qpIns" title="Insertar otro PDF junto a esta página"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9z"/><path d="M13 3v6h6"/><path d="M12 13v6M9 16h6"/></svg> Insertar PDF</button>
<input type="file" id="qpInsFile" accept="application/pdf" hidden>
<span class="pbsep"></span>
<button class="qa" id="qpRotL" title="Girar esta página a la izquierda"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg> Izquierda</button>
<button class="qa" id="qpRotR" title="Girar esta página a la derecha"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg> Derecha</button>
<span class="pbsep"></span>
<button class="qa" id="qpExt" title="Descargar solo esta página como PDF"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.12 15.88"/><path d="M14.47 14.48L20 20"/><path d="M8.12 8.12L12 12"/></svg> Extraer esta página</button>
<button class="qa" id="qpDel" title="Borrar únicamente esta página"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-14"/><path d="M10 11v6M14 11v6"/></svg> Borrar</button>
<span class="pbsep"></span>
<button class="qa" id="qpUndo" title="Deshacer el último cambio (Ctrl+Z)"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg> Deshacer</button>
<button class="qa" id="qpRedo" title="Rehacer el cambio deshecho (Ctrl+Y)"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 14 20 9 15 4"/><path d="M4 20v-7a4 4 0 0 1 4-4h12"/></svg> Rehacer</button></div>
</div>
<div id="mgDlg"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🔗 Unir archivos PDF</div>
<div style="font-size:13px;color:var(--mut)">Añade los PDF, arrástralos para ordenarlos y confirma. Se unen en ese orden exacto.</div>
<div id="mgList" style="margin-top:8px"></div>
<div style="margin-top:10px"><label class="bigbtn" style="display:inline-flex"><span class="ic">➕</span>Añadir archivos…<input type="file" id="mgFiles" accept="application/pdf" multiple hidden></label><button id="mgBoardBtn" type="button" style="margin-left:8px">🧩 Ordenar en bloques</button></div>
<div id="mgBoard" style="display:none;margin-top:10px"></div>
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
<div id="certDlg"><div class="box" style="width:920px;max-width:96vw">
<h3 style="margin:0 0 4px">🎓 Certificados en bloque</h3>
<p style="margin:0 0 8px;color:#475569;font-size:12.5px"><b>1.</b> Elige tu certificado modelo. <b>2.</b> Haz <b>clic en el modelo</b> donde va cada dato (el nombre, el curso, la fecha…): cada clic crea un Dato. <b>3.</b> Descarga la plantilla Excel, llénala (una fila = un certificado) y súbela. <b>4.</b> Genera: sale un ZIP con un PDF por fila.</p>
<div style="display:flex;gap:8px;align-items:center;margin-bottom:6px;flex-wrap:wrap"><button id="certTplBtn">Elegir modelo PDF</button><span id="certTplName" style="font-size:12.5px;color:#334155">Ningún archivo</span><span id="certScanInfo" style="font-size:12.5px;color:#64748B"></span></div>
<input type="file" id="certTplFile" accept=".pdf,application/pdf" style="display:none">
<div id="certMapWrap" style="display:none">
<div style="display:flex;gap:8px;align-items:center;margin:6px 0;flex-wrap:wrap"><button id="certPrev">◀</button><span id="certPgLbl" style="font-size:12.5px"></span><button id="certNext">▶</button><span style="font-size:12.5px;color:#64748B">Haz clic en el certificado para ubicar un dato en ese punto.</span></div>
<div id="certStage" style="background:#E2E8F0;border:1px solid #CBD5E1;border-radius:8px;overflow:auto;max-height:46vh;text-align:center"><div id="certStageInner" style="position:relative;display:inline-block"><img id="certMap" style="max-width:100%;cursor:crosshair;display:block"></div></div>
<div id="certFields" style="margin-top:8px"></div>
</div>
<div style="display:flex;gap:8px;align-items:center;margin:10px 0 8px;flex-wrap:wrap"><button id="certXlBtn">Elegir base Excel (.xlsx)</button><span id="certXlName" style="font-size:12.5px;color:#334155">Ningún archivo</span><button id="certTplXl" disabled>⬇ Descargar plantilla Excel</button></div>
<input type="file" id="certXlFile" accept=".xlsx" style="display:none">
<div id="certInfo" style="font-size:12.5px;color:#475569;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;min-height:34px">Elige el modelo: si tu certificado ya trae datos como {{nombre}} se detectan solos; si no, ubícalos con clics.</div>
<div style="display:flex;gap:14px;align-items:center;margin-top:10px;flex-wrap:wrap"><label style="font-size:12.5px;color:#334155">Nombrar cada PDF con <select id="certNameCol"></select></label><label style="font-size:12.5px;color:#334155">¿Cuántos generar? <select id="certLimitSel"><option value="0">Todos</option><option value="n">Solo los primeros</option></select> <input type="number" id="certLimitN" value="10" min="1" style="width:64px;display:none"></label></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="certGo" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700" disabled>Generar certificados</button><button id="certCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="objDlg"><div class="box" style="width:400px;max-width:92vw">
<h3 id="objTitle" style="margin:0 0 6px">Objeto seleccionado</h3>
<p id="objDesc" style="margin:0;color:#475569;font-size:13px"></p>
<div id="objWrite" style="display:none;margin-top:12px"><div style="font-size:13px;color:#334155;margin-bottom:6px"><b>Escribir sobre la línea</b> (rellenar el espacio):</div><div style="display:flex;gap:8px;align-items:center"><input type="text" id="objText" placeholder="Texto que va sobre la línea" style="flex:1"><label style="font-size:12.5px;color:#334155">Tamaño <input type="number" id="objTextSize" value="11" min="6" max="40" style="width:56px"></label></div><button id="objWriteBtn" style="margin-top:8px;width:100%;background:#059669;color:#fff;border-color:#059669;font-weight:700">✍️ Escribir en la línea</button></div>
<div id="objOpts" style="display:none;margin-top:12px;gap:12px;align-items:center;flex-wrap:wrap"><label style="font-size:13px;color:#334155">Color <input type="color" id="objColor" value="#000000"></label><label style="font-size:13px;color:#334155">Grosor <input type="number" id="objWidth" min="0.3" max="12" step="0.25" value="1" style="width:64px"></label><button id="objApply" style="background:var(--az);color:#fff;border-color:var(--az);font-weight:700">✔ Aplicar cambios</button></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="objDel" style="flex:1;background:#DC2626;color:#fff;border-color:#DC2626;font-weight:700">🗑️ Borrar objeto</button><button id="objCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="multiDlg"><div class="box" style="width:430px;max-width:92vw">
<h3 style="margin:0 0 6px">Varios PDF</h3>
<p id="multiTxt" style="margin:0;color:#475569;font-size:13px"></p>
<div style="margin-top:14px;display:flex;flex-direction:column;gap:8px"><button id="multiLoad" style="background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Solo cargar (en ese orden)</button><button id="multiOrder" style="font-weight:700">Ordenar primero</button><button id="multiCancel">Cancelar</button></div>
</div></div>
<div id="openChoiceDlg"><div class="box" style="width:440px;max-width:92vw">
<h3 style="margin:0 0 6px">Ya hay un documento abierto</h3>
<p id="ocTxt" style="margin:0;color:#475569;font-size:13px"></p>
<div style="margin-top:14px;display:flex;flex-direction:column;gap:8px"><button id="ocAdd" style="background:var(--az);color:#fff;border-color:var(--az);font-weight:700">➕ Añadir al documento actual</button><button id="ocReplace" style="font-weight:700">🔄 Reemplazar el documento actual</button><button id="ocCancel">Cancelar</button></div>
</div></div>
<div id="poDlg"><div class="box" style="width:880px;max-width:95vw">
<h3 style="margin:0 0 4px">Ordenar páginas</h3>
<p style="margin:0 0 8px;color:#475569;font-size:13px">Arrastra los bloques para cambiar el orden de las páginas del documento. Cada bloque dice qué página es y en qué posición quedará. Si acercas un bloque al borde de arriba o de abajo, el tablero se desplaza solo.</p>
<div id="poGrid" class="mggrid" style="overflow:auto;max-height:60vh;padding:2px"></div>
<div style="margin-top:12px;display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap"><button id="poReset">↩️ Orden original</button><button id="poCancel">Cancelar</button><button id="poOk" style="background:var(--az);color:#fff;border-color:var(--az);font-weight:700">✔ Aplicar orden</button></div>
</div></div>
<div id="rotDlg"><div class="box" style="width:400px;max-width:92vw">
<h3 id="rotTitle" style="margin:0 0 6px">Girar páginas</h3>
<label style="display:block;margin:7px 0;cursor:pointer"><input type="radio" name="rotScope" value="all" checked> Todas las páginas</label>
<label style="display:block;margin:7px 0;cursor:pointer"><input type="radio" name="rotScope" value="range"> Solo un rango: desde la página <input type="number" id="rotFrom" min="1" value="1" style="width:64px"> hasta la <input type="number" id="rotTo" min="1" value="1" style="width:64px"></label>
<p id="rotInfo" style="margin:6px 0;color:#475569;font-size:12.5px"></p>
<div style="margin-top:12px;display:flex;gap:8px;justify-content:flex-end"><button id="rotCancel">Cancelar</button><button id="rotOk" style="background:var(--az);color:#fff;border-color:var(--az);font-weight:700">✔ Girar</button></div>
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
<div id="cpEst" style="font-size:13px;color:#334155;margin-top:8px"></div>
<div style="font-size:13px;color:var(--mut);margin-top:8px">En documentos grandes puede tardar varios minutos.</div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="cpOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">🗜️ Comprimir</button><button id="cpCancel">Cancelar</button></div>
</div></div>
<div id="progDlg"><div class="box">
<div id="progTitle" style="font-size:16.5px;font-weight:700;margin-bottom:4px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">Trabajando…</div>
<div id="progLabel" style="font-size:13px;color:var(--mut)">Preparando…</div>
<div style="background:#E2E8F0;border-radius:999px;height:16px;overflow:hidden;margin-top:12px"><div id="progFill" style="background:var(--az);height:100%;width:0%;border-radius:999px;transition:width .3s"></div></div>
<div style="display:flex;justify-content:space-between;margin-top:8px;font-size:13.5px;color:#334155"><span id="progPct" style="font-weight:700">0%</span><span id="progEta">calculando tiempo…</span></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="progCancel" style="flex:1">Cancelar la tarea</button></div>
</div></div>
<div id="msgDlg" style="z-index:90"><div class="box">
<div id="msgTitle" style="font-size:16.5px;font-weight:700;margin-bottom:6px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">Aviso</div>
<div id="msgText" style="font-size:14px;color:#334155;line-height:1.5;white-space:pre-wrap"></div>
<div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px"><button id="msgOk" style="background:var(--az);color:#fff;border-color:var(--az);font-weight:700;padding:9px 26px">Aceptar</button></div>
</div></div>
<div id="openPwDlg" style="z-index:95"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:6px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🔒 PDF protegido</div>
<div style="font-size:14px;color:#334155;line-height:1.5">Este PDF está protegido con contraseña. Escríbela para abrirlo:</div>
<input type="password" id="openPwIn" placeholder="Contraseña del PDF" style="width:100%;margin-top:10px;padding:9px 11px;border-radius:9px;border:1px solid var(--line);font-size:14.5px">
<div style="margin-top:14px;display:flex;gap:8px"><button id="openPwOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Abrir el PDF</button><button id="openPwCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="decDlg" style="z-index:95"><div class="box">
<div style="font-size:16.5px;font-weight:700;margin-bottom:6px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">🔓 Quitar la contraseña</div>
<div style="font-size:13.5px;color:var(--mut)">Escribe la contraseña actual del PDF. Si es la correcta, quedará sin protección.</div>
<input type="password" id="decPwIn" placeholder="Contraseña actual" style="width:100%;box-sizing:border-box;margin-top:12px;padding:10px 12px;border:1px solid var(--line);border-radius:9px;font-size:14px">
<div style="margin-top:14px;display:flex;gap:8px"><button id="decOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Quitar la contraseña</button><button id="decCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="txtDlg" style="z-index:85"><div class="box" style="width:min(860px,94vw)">
<div style="font-size:16.5px;font-weight:700;margin-bottom:6px;font-family:'Plus Jakarta Sans','Segoe UI',sans-serif">Texto completo</div>
<textarea id="txtBig" rows="18" style="width:100%;font-size:14px;line-height:1.55" readonly></textarea>
<div style="margin-top:12px;display:flex;gap:8px"><button id="txtCopy" style="flex:1">📋 Copiar el texto</button><button id="txtClose" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Cerrar</button></div>
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
<div id="pgSecBoard" class="pgsec" style="display:none"><div style="display:flex;gap:8px;align-items:center"><button id="pgBoardBtn" type="button">🧩 Elegir páginas en bloques</button><span id="pgBoardInfo" style="font-size:12.5px;color:var(--mut)"></span></div>
<div id="pgBoard" style="display:none;margin-top:8px;max-height:290px;overflow:auto;border:1px solid var(--line);border-radius:10px;padding:8px"></div></div>
<div style="margin-top:14px;display:flex;gap:8px"><button id="pgOk" style="flex:1;background:var(--az);color:#fff;border-color:var(--az);font-weight:700">Aceptar</button><button id="pgCancel" style="flex:1">Cancelar</button></div>
</div></div>
<div id="insDlg"><div class="box"><div style="font-size:16px;font-weight:600;margin-bottom:6px">¿Dónde inserto el otro PDF?</div>
<div style="font-size:13.5px;color:var(--mut)">Elige la página y si el otro PDF va antes o después de ella</div>
<div style="margin:10px 0;font-size:14px">Página: <input type="number" id="insPage" value="1" min="1" style="width:72px;padding:6px 8px;border-radius:7px;border:1px solid var(--line)"> <span id="insTotal" style="color:var(--mut);font-size:12.5px"></span></div>
<button id="insBefore">⬆ Antes de esa página</button>
<button id="insAfter">⬇ Después de esa página</button>
<button id="insCancel">Cancelar</button></div></div>
<div id="editBar"><span>✏️ <b>Editando línea:</b></span><input type="text" id="editInput"><button id="edB" title="Negrita"><b>N</b></button><button id="edI" title="Cursiva"><i>C</i></button><button id="edU" title="Subrayado"><u>S</u></button><button id="edS" title="Tachado"><s>T</s></button><select id="edFont" title="Tipo de letra"><option value="">Letra: automática</option><option value="helv">Helvetica</option><option value="tiro">Times</option><option value="cour">Courier</option></select><input type="number" id="edSize" min="5" max="96" step="0.5" title="Tamaño de letra"><input type="color" id="edColor" value="#000000" title="Color del texto"><label style="font-size:12.5px" title="Poner un fondo de color detrás del texto"><input type="checkbox" id="edBgOn"> Fondo</label><input type="color" id="edBg" value="#ffeb3b" title="Color de fondo / resaltado"><button id="editOk">✔ Aplicar</button><button id="editCancel">Cancelar</button></div>
<div id="imgBar"><span>🖼️ <b>Imagen en la pág. <span id="imgBarPg">1</span>:</b></span><label>Ángulo <input type="range" id="imAng" min="-180" max="180" value="0" style="width:88px"></label><label>Tamaño <input type="range" id="imSize" min="5" max="100" value="30" style="width:76px"></label><label>Brillo <input type="range" id="imBr" min="40" max="160" value="100" style="width:66px"></label><label>Contraste <input type="range" id="imCt" min="40" max="160" value="100" style="width:66px"></label><button id="imRot90">⟳ 90°</button><button id="imRepl">Reemplazar</button><button id="imOk">✔ Aplicar</button><button id="imCancel">✖ Quitar</button></div>
<div id="pvDlg" style="display:none;position:fixed;inset:0;background:rgba(10,12,20,.9);z-index:95;flex-direction:column"><div style="display:flex;gap:8px;align-items:center;padding:10px 14px"><b style="color:#fff">Vista previa en grande</b><span style="flex:1"></span><button id="pvOut" class="pvb">− Zoom</button><button id="pvIn" class="pvb">+ Zoom</button><button id="pvFull" class="pvb">⛶ Pantalla completa</button><button id="pvClose" class="pvb">✖ Cerrar</button></div><div style="flex:1;overflow:auto;padding:6px"><img id="pvImg" style="width:100%;background:#fff;border-radius:4px;display:block;margin:0 auto"></div></div>
<div id="pageScroll">
<div id="pagesBox"></div>
<div class="empty" id="emptyMsg"><button id="emptyPlus" title="Abrir PDF (puedes elegir varios a la vez)">+</button><div>Abre un PDF con el botón «Abrir PDF» de la pestaña Archivo<br>o arrastra los archivos hasta aquí (pueden ser varios).<br><span style="font-size:13.5px">Créditos: Luis Aven</span></div></div>
</div>
</div>
<aside id="side"><button id="sideMin" title="Minimizar: ocultar los datos del documento">—</button><h3>Datos del documento</h3><div id="infoBox">Sin documento cargado.</div></aside>
<button id="sideTab" title="Mostrar los datos del documento" style="display:none">❮</button>
</main>
<div class="statusbar"><span id="status">Listo.</span></div>

<script>
let cur=null, curName="documento.pdf", page=0, pages=0, zoom=1.4;
let curDocId=null, pageSizes=[], curSizeKB=0; const docIds=new Map();
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
function status(msg,ok=true){ if(ok===false){ showErr(msg); return; } const s=$("status");s.textContent=msg;s.className="ok"; }
function showErr(msg){ sfx("err"); $("msgTitle").textContent="⚠️ Aviso"; $("msgText").textContent=String(msg||"Ocurrió un error"); $("msgDlg").style.display="flex"; }
$("msgOk").onclick=()=>{ $("msgDlg").style.display="none"; };
function clearTxt(){ const t=$("txtOut"); if(t)t.value=""; }
async function ensureBytes(){ if(!cur && curDocId){ const f=await call("/api/fetch_doc",{doc_id:curDocId}); cur=f.pdf; docIds.set(cur,curDocId); } }
function readB64(f){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result.split(",")[1]);r.onerror=rej;r.readAsDataURL(f);});}
async function call(path,payload){
  if(payload && payload.pdf && payload.pdf===cur && curDocId){ payload=Object.assign({},payload,{doc_id:curDocId,light:1}); delete payload.pdf; }
  else if(payload && "pdf" in payload && !payload.pdf && curDocId){ payload=Object.assign({},payload,{doc_id:curDocId,light:1}); delete payload.pdf; }
  const ctl=new AbortController(); window._curAbort=ctl;
  try{
    const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload),signal:ctl.signal});
    const j=await r.json(); if(!r.ok||j.error) throw new Error(j.error||("HTTP "+r.status));
    if(j && j.doc_id && j.pdf){ docIds.set(j.pdf,j.doc_id); if(docIds.size>30)docIds.delete(docIds.keys().next().value); }
    return j;
  }catch(e){ if(e && e.name==="AbortError") throw new Error("Cancelado por el usuario"); throw e; }
  finally{ if(window._curAbort===ctl) window._curAbort=null; }
}
let docPw="";
let progCancelWanted=false, progT0=0, progTimer=null, progDepth=0, progThr=1000, progShown=false, progJobId=null, progJobKnown=false, progLabelTxt="Procesando";
$("progCancel").onclick=()=>{ if(progJobId){ progCancelWanted=true; } else if(window._curAbort){ try{ window._curAbort.abort(); }catch(e){} } };
function runQ(fn){ return run(fn, undefined, 2500); }
let _AC=null;
function sfx(kind){ try{ _AC=_AC||new (window.AudioContext||window.webkitAudioContext)(); if(_AC.state==="suspended")_AC.resume();
  const t=_AC.currentTime;
  const tone=(f,t0,dur,type,vol)=>{ const o=_AC.createOscillator(),g=_AC.createGain(); o.type=type; o.frequency.value=f;
    g.gain.setValueAtTime(0.0001,t0); g.gain.exponentialRampToValueAtTime(vol,t0+0.015); g.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
    o.connect(g); g.connect(_AC.destination); o.start(t0); o.stop(t0+dur+0.05); };
  if(kind==="ok"){ tone(660,t,0.12,"sine",0.045); tone(880,t+0.09,0.16,"sine",0.045); }
  else if(kind==="err"){ tone(196,t,0.22,"triangle",0.055); }
  else if(kind==="info"){ tone(520,t,0.1,"sine",0.03); }
}catch(e){} }
function fmtT(s){ if(s==null||s===undefined)return "calculando tiempo…"; s=Math.max(0,Math.round(s)); if(s<60)return "quedan ~"+s+" s"; const m=Math.floor(s/60),ss=s%60; return "quedan ~"+m+":"+(ss<10?"0":"")+ss+" min"; }
function progPaintIndet(){ const el=Math.max(0,Math.round((Date.now()-progT0)/1000)); $("progFill").style.width="45%"; $("progPct").textContent="…"; $("progLabel").textContent="Trabajando… ("+el+" s transcurridos)"; $("progEta").textContent="El tiempo depende del tamaño del archivo."; }
function progShow(label){ $("progTitle").textContent="⏳ "+label; progShown=true; progPaintIndet(); $("progDlg").style.display="flex"; }
function busyStart(label, thr){ progDepth++; if(label)progLabelTxt=label; if(progDepth===1){ progThr=thr||1000; progT0=Date.now(); progCancelWanted=false; progJobId=null; progJobKnown=false;
  progTimer=setInterval(()=>{ if(!progShown && Date.now()-progT0>=progThr && !anyDlgOpen()) progShow(progLabelTxt); else if(progShown && !progJobKnown) progPaintIndet(); },250); } }
function busyEnd(){ if(progDepth>0)progDepth--; if(progDepth===0){ if(progTimer)clearInterval(progTimer); progTimer=null; progShown=false; progJobId=null; progJobKnown=false; $("progDlg").style.display="none"; } }
function anyDlgOpen(){ return ["mgDlg","svDlg","pwDlg","ciDlg","xiDlg","scDlg","dkDlg","cfDlg","cpDlg","msgDlg","openPwDlg","txtDlg","dlDlg","pgDlg","insDlg","decDlg","certDlg","objDlg","multiDlg","openChoiceDlg","poDlg","rotDlg"].some(id=>{ const e=$(id); return e && e.style.display==="flex"; }); }
let progBlurHidden=false;
window.addEventListener("blur",()=>{ if(progShown){ $("progDlg").style.display="none"; progBlurHidden=true; } });
window.addEventListener("focus",()=>{ if(progBlurHidden){ progBlurHidden=false; if(progDepth>0 && progShown)$("progDlg").style.display="flex"; } });
function updProg(s){ progJobKnown=true; const p=s.pct||0; $("progFill").style.width=p+"%"; $("progPct").textContent=p+"%"; $("progLabel").textContent="Procesando… ("+s.elapsed+" s transcurridos)"; $("progEta").textContent=fmtT(s.eta); }
async function callLong(path,payload,label){
  busyStart(label);
  try{
    let args=payload;
    if(args && args.pdf && args.pdf===cur && curDocId){ args=Object.assign({},args,{doc_id:curDocId}); delete args.pdf; }
    else if(args && "pdf" in args && !args.pdf && curDocId){ args=Object.assign({},args,{doc_id:curDocId}); delete args.pdf; }
    const st=await call("/api/job_start",{op:path,args});
    progJobId=st.job;
    while(true){
      await new Promise(r=>setTimeout(r,450));
      if(progCancelWanted){ progCancelWanted=false; try{ await call("/api/job_cancel",{job:st.job}); }catch(e){} throw new Error("Cancelado por el usuario"); }
      const s=await call("/api/job_status",{job:st.job});
      if(s.done){ if(s.error) throw new Error(s.error); if(progShown)sfx("ok"); const j=s.result;
        if(j && j.doc_id && j.pdf){ docIds.set(j.pdf,j.doc_id); if(docIds.size>30)docIds.delete(docIds.keys().next().value); }
        return j; }
      if(s.known && progShown) updProg(s);
      else if(s.known){ progJobKnown=true; }
    }
  } finally { progJobId=null; busyEnd(); }
}
function b64ToBlob(b64,mime="application/pdf"){
  const bin=atob(b64),arr=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);
  return new Blob([arr],{type:mime});
}
let dlNote="";
async function saveB64(b64,name,mime="application/pdf"){
  const a=document.createElement("a");a.className="dl";a.download=name;
  a.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" style="vertical-align:-2px"><path fill="#ffffff" d="M11 2.5h2V9h3.4L12 14.6 7.6 9H11z"/><path fill="#ffffff" d="M4.5 15.4v2.9c0 1 .8 1.8 1.8 1.8h11.4c1 0 1.8-.8 1.8-1.8v-2.9h-2.7v2.7H7.2v-2.7z"/></svg> Descargar';
  let stUrl=null;
  try{ const st=await call("/api/stage_download",{data:b64,name,mime}); stUrl=st.url; }catch(e){ }
  a.href="#";
  a.onclick=async ev=>{ ev.preventDefault(); if(a.dataset.busy)return; a.dataset.busy="1";
    try{ let blob=null;
      if(stUrl){ const r=await fetch(stUrl); if(r.ok)blob=await r.blob(); }
      if(!blob)blob=b64ToBlob(b64,mime);
      const u=URL.createObjectURL(blob); const t=document.createElement("a");
      t.href=u; t.download=name; document.body.appendChild(t); t.click(); t.remove();
      setTimeout(()=>URL.revokeObjectURL(u),4000);
    }catch(e){ showErr("No se pudo descargar: "+e.message); }
    a.dataset.busy=""; };
  $("dlName").textContent=name;
  $("dlMsg").textContent=dlNote||"Tu archivo está listo."; dlNote="";
  const slot=$("dlSlot"); slot.innerHTML=""; slot.appendChild(a);
  $("dlDlg").style.display="flex"; sfx("ok");
}
$("dlClose").onclick=()=>{ $("dlDlg").style.display="none"; };
function versionedName(){ dlVer++; const base=curName.replace(/\.pdf$/i,""); return base+"_AvenPDF_v"+String(dlVer).padStart(2,"0")+".pdf"; }
async function downloadCurrent(){ if(!cur && !curDocId){ showErr("Primero abre un PDF."); return; } await ensureBytes(); const nm=versionedName(); dlNote="Copia v"+String(dlVer).padStart(2,"0")+" del documento: el archivo original no se tocó."; saveB64(cur,nm); status("Copia v"+String(dlVer).padStart(2,"0")+" lista para descargar ✔"); }
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
function pendingStrokes(){ try{ return (typeof drawStrokes!=="undefined"&&drawPageNow>=0)?(drawStrokes[drawPageNow]||[]).length:0; }catch(_){ return 0; } }
function updHist(){ const u=$("qpUndo"),r=$("qpRedo"); if(u)u.disabled=!(histU.length||pendingStrokes()); if(r)r.disabled=!histR.length; }
async function setCurrent(b64,name,stayPage){
  const prevPage=page;
  if((cur||curDocId) && b64!==cur && !histJump){ histU.push({doc_id:curDocId,name:curName,page:prevPage}); if(histU.length>25)histU.shift(); histR=[]; }
  clearDownloads();
  cur=b64; if(name)curName=name;
  curDocId=docIds.get(b64)||null;
  let info;
  if(curDocId) info=await call("/api/info",{doc_id:curDocId,password:docPw});
  else{ info=await call("/api/open",{pdf:cur,password:docPw}); if(info.doc_id){ curDocId=info.doc_id; docIds.set(b64,curDocId); } }
  pages=info.pages; pageSizes=info.page_sizes||[]; curSizeKB=info.size_kb||0; clearTxt(); $("emptyMsg").style.display="none";
  page=stayPage?prevPage:0;
  if(page>=pages)page=pages-1; if(page<0)page=0;
  lastToc=info.toc||[]; renderToc();
  $("infoBox").textContent=`Archivo: ${curName}\nPáginas: ${info.pages}\nTamaño: ${fmtSize(info.size_kb)}\nTítulo: ${info.title||"—"}\nAutor: ${info.author||"—"}\nCreador: ${info.creator||"—"}\nMarcadores: ${info.bookmarks}${info.encrypted?"\n🔒 Protegido con contraseña":""}`;
  $("bDownload").disabled=false; $("bClose").disabled=false; $("bSave").disabled=false; dirty=true;
  await renderAll(); await buildThumbs(); gotoPage(page,false); updHist();
}
async function adopt(j,name,stayPage){
  if(j && j.pdf){ await setCurrent(j.pdf, name, stayPage); return; }
  if(j && j.doc_id){ await adoptById(j.doc_id,name,stayPage); return; }
}
async function adoptById(docId,name,stayPage){
  const prevPage=page;
  if(curDocId && docId!==curDocId && !histJump){ histU.push({doc_id:curDocId,name:curName,page:prevPage}); if(histU.length>25)histU.shift(); histR=[]; }
  clearDownloads();
  cur=null; if(name)curName=name; curDocId=docId;
  const info=await call("/api/info",{doc_id:curDocId,password:docPw});
  pages=info.pages; pageSizes=info.page_sizes||[]; curSizeKB=info.size_kb||0; clearTxt(); $("emptyMsg").style.display="none";
  page=stayPage?prevPage:0;
  if(page>=pages)page=pages-1; if(page<0)page=0;
  lastToc=info.toc||[]; renderToc();
  $("infoBox").textContent=`Archivo: ${curName}\nPáginas: ${info.pages}\nTamaño: ${fmtSize(info.size_kb)}\nTítulo: ${info.title||"—"}\nAutor: ${info.author||"—"}\nCreador: ${info.creator||"—"}\nMarcadores: ${info.bookmarks}${info.encrypted?"\n🔒 Protegido con contraseña":""}`;
  $("bDownload").disabled=false; $("bClose").disabled=false; $("bSave").disabled=false; dirty=true;
  await renderAll(); await buildThumbs(); gotoPage(page,false); updHist();
}
let lastPix=null;
let renderGen=0; let prevImgs={}, prevThumbs={};
async function renderAll(){
  if(editSel){ editSel=null; closeEditBar(); }
  if(!cur && !curDocId)return;
  const zp=$("zPct"); if(zp)zp.textContent=Math.round(zoom*100)+"%";
  const gen=++renderGen;
  const box=$("pagesBox"); const keepImgs={}; box.querySelectorAll("img.cpage").forEach(im=>{ if(im.src) keepImgs[im.dataset.i]=im.src; }); prevImgs=keepImgs; box.innerHTML="";
  if(pgObs)pgObs.disconnect(); loadQ=[];
  pgObs=new IntersectionObserver(es=>{ es.forEach(en=>{ if(en.isIntersecting) queueLoad(en.target); }); },{root:$("pageScroll"),rootMargin:"700px 0px"});
  for(let i=0;i<pages;i++){
    const sz=pageSizes[i]||pageSizes[0]||[595,842];
    const wrap=document.createElement("div"); wrap.className="pgwrap"; wrap.dataset.pg=i;
    wrap.style.width=Math.round(sz[0]*zoom)+"px"; wrap.style.height=Math.round(sz[1]*zoom)+"px";
    if(prevImgs[i]){ wrap.appendChild(mkPageImg(prevImgs[i],i)); } else { const ph=document.createElement("div"); ph.className="pgload"; ph.textContent="Página "+(i+1); wrap.appendChild(ph); }
    wrap.onclick=()=>{ page=i; syncLabel(); };
    box.appendChild(wrap); pgObs.observe(wrap);
  }
  syncLabel();
  requestAnimationFrame(()=>gotoPage(page,false));
}
function queueLoad(wrap){ if(wrap.dataset.done||wrap.dataset.queued)return; wrap.dataset.queued="1"; loadQ.push(wrap); pumpQ(); }
function pumpQ(){ while(loadActive<4&&loadQ.length){ const w=loadQ.shift(); loadActive++; loadPageImg(w).finally(()=>{ loadActive--; pumpQ(); }); } }
function mkPageImg(src,i){ const im=document.createElement("img"); im.className="cpage"; im.src=src; im.dataset.i=i;
  im.onclick=(ev)=>{ page=i; syncLabel(); if(editMode) pickLine(ev,im,i); };
  if(editMode) im.style.cursor="text"; return im; }
async function loadPageImg(wrap){
  const i=+wrap.dataset.pg, gen=renderGen;
  try{
    const rz=editMode?Math.min(zoom*2,3.4):zoom;
    const j=await call("/api/render",{doc_id:curDocId,page:i,zoom:rz,password:docPw});
    if(gen!==renderGen)return;
    if(i===0)lastPix={w:j.w,h:j.h,zoom};
    const url="data:image/png;base64,"+j.png;
    const old=wrap.querySelector("img.cpage");
    if(old){ const pre=new Image(); pre.onload=()=>{ old.src=url; }; pre.onerror=()=>{ old.src=url; }; pre.src=url; }
    else { wrap.innerHTML=""; wrap.appendChild(mkPageImg(url,i)); }
    wrap.dataset.done="1";
  }catch(e){ wrap.innerHTML=""; const d=document.createElement("div"); d.className="pgload"; d.textContent="No se pudo cargar la página "+(i+1); wrap.appendChild(d); }
}
function syncThumbs(){ paintThSel(); document.querySelectorAll("#thumbList .titem").forEach((w,k)=>{ const im=w.querySelector("img"); if(im)im.classList.toggle("sel",k===page); }); }
function syncLabel(){
  $("pgLabel").textContent=pages?`Página ${page+1} de ${pages}`:"—";
  document.querySelectorAll(".pgwrap").forEach(im=>{ im.style.outline=(+im.dataset.pg===page)?"3px solid var(--acc)":"none"; });
  syncThumbs();
  drawAttach(); imgAttach();
}
document.addEventListener("keydown",e=>{
  const t=e.target; if(!t||t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.tagName==="SELECT"||t.isContentEditable) return;
  if(!pages) return;
  if(e.key==="ArrowRight"){ if(page<pages-1){ e.preventDefault(); gotoPage(page+1); } }
  else if(e.key==="ArrowLeft"){ if(page>0){ e.preventDefault(); gotoPage(page-1); } }
});
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
  const box=$("thumbList"); const keepT={}; box.querySelectorAll(".titem img").forEach(im=>{ const w=im.closest(".titem"); if(w) keepT[w.dataset.idx]=im.src; }); prevThumbs=keepT; box.innerHTML="";
  if(thObs)thObs.disconnect();
  thObs=new IntersectionObserver(es=>{ es.forEach(en=>{ if(en.isIntersecting) loadThumb(en.target); }); },{root:$("thumbs"),rootMargin:"500px 0px"});
  for(let i=0;i<pages;i++){
    const s=pageSizes[i]||pageSizes[0]||[595,842]; const h=Math.round(110*s[1]/Math.max(1,s[0]));
    const wrap=document.createElement("div"); wrap.className="titem"; wrap.draggable=true; wrap.dataset.idx=i;
    const ph=document.createElement("div"); ph.className="tph"; ph.style.height=h+"px"; ph.textContent="…";
    const num=document.createElement("div"); num.className="tnum"; num.textContent=(i+1);
    wrap.appendChild(ph); wrap.appendChild(num); box.appendChild(wrap); wrap._ph=ph;
    if(prevThumbs[i]){ const pim=document.createElement("img"); pim.src=prevThumbs[i]; pim.onclick=()=>{ const idx=[...$("thumbList").querySelectorAll(".titem")].indexOf(wrap); if(idx>=0)gotoPage(idx); }; ph.replaceWith(pim); wrap._ph=pim; }
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
        await adopt(j,curName,true); page=to; gotoPage(to,false); syncLabel();
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
    const j=await call("/api/render",{doc_id:curDocId,page:i,zoom:0.22,password:docPw});
    if(gen!==thumbGen)return;
    const url="data:image/png;base64,"+j.png; const oldT=wrap.querySelector("img");
    if(oldT){ const pre=new Image(); pre.onload=()=>{ oldT.src=url; }; pre.onerror=()=>{ oldT.src=url; }; pre.src=url; }
    else { const im=document.createElement("img"); im.src=url;
    im.onclick=()=>{ const idx=[...$("thumbList").querySelectorAll(".titem")].indexOf(wrap); if(idx>=0)gotoPage(idx); };
    if(wrap._ph) wrap._ph.replaceWith(im); }
  }catch(e){ }
}
function hasDoc(){ return !!(cur||curDocId); }
async function need(){ if(!cur && !curDocId){ gotoTab("inicio"); throw new Error("Primero abre un PDF (pestaña Archivo)."); } }
async function run(fn,msg,thr){ busyStart("Procesando",thr); try{ clearDownloads(); status("Procesando…"); await fn(); if(msg)status(msg); else if($("status").textContent==="Procesando…") status("Listo ✔"); }catch(e){ if(e && e.message==="Cancelado por el usuario"){ status("Cancelado."); setTimeout(()=>{ if($("status").textContent==="Cancelado.") status("Listo."); },2600); } else { status("Listo."); showErr(e.message); } } finally{ busyEnd(); } }
function wipeViewer(msg){
  renderGen++; thumbGen++; if(pgObs)pgObs.disconnect(); if(thObs)thObs.disconnect(); loadQ=[];
  prevImgs={}; prevThumbs={}; thSel.clear(); $("pagesBox").innerHTML=""; $("thumbList").innerHTML=""; $("tocList").innerHTML="";
  $("pgLabel").textContent="—"; $("emptyMsg").style.display="block"; status(msg||"Listo.");
}
let pendingOpen=null;
function resetWorkspace(){ // al abrir un PDF nuevo no queda nada del anterior
  prevImgs={}; prevThumbs={};
  clearTxt();
  docPw="";
  histU=[]; histR=[]; updHist();
  mgItems=[]; renderMg();
  ciItems=[]; renderCi();
  ["noteText","wmText","replTxt"].forEach(id=>{ const el=$(id); if(el)el.value=""; });
  if(editMode){ editMode=false; editSel=null; $("bEditMode").classList.remove("activo"); $("editBar").style.display="none"; }
  clearDownloads();
}
async function tryOpen(b64,name,okMsg,fresh=true){ if(fresh)resetWorkspace();
  try{ await setCurrent(b64,name); dirty=false; dlVer=0; if(okMsg)status(okMsg); }
  catch(e){ if(/contraseña|protegido/i.test(e.message||"")){ pendingOpen={b64,name,okMsg}; $("openPwIn").value=""; $("openPwDlg").style.display="flex"; setTimeout(()=>$("openPwIn").focus(),60); } else throw e; } }
$("openPwOk").onclick=()=>{ docPw=$("openPwIn").value; $("openPwDlg").style.display="none";
  if(pendingOpen){ const p=pendingOpen; pendingOpen=null; run(async()=>{ await tryOpen(p.b64,p.name,p.okMsg,false); }); } };
$("openPwCancel").onclick=()=>{ $("openPwDlg").style.display="none"; pendingOpen=null; cur=null; curDocId=null; wipeViewer("Apertura cancelada: el PDF necesita su contraseña."); };
$("openPwIn").addEventListener("keydown",e=>{ if(e.key==="Enter")$("openPwOk").click(); });
$("file").addEventListener("change",async e=>{ const fs=[...e.target.files]; e.target.value=""; if(!fs.length)return;
  if(fs.length===1 && !(cur||curDocId)){ singleOpen(fs[0]); return; }
  fileHandle=null; handleChosenFiles(fs); });
document.getElementById('bOpenLbl').addEventListener("click",async e=>{
  if(!window.showOpenFilePicker) return;
  e.preventDefault();
  try{
    const hs=await window.showOpenFilePicker({types:[{description:"PDF",accept:{"application/pdf":[".pdf"]}}],multiple:true});
    const fs=[]; for(const h of hs)fs.push(await h.getFile());
    if(hs.length===1 && !(cur||curDocId)){ const h=hs[0]; fileHandle=h; try{ await h.requestPermission({mode:"readwrite"}); }catch(_){ }
      wipeViewer("Cargando "+fs[0].name+"…");
      run(async()=>{ await tryOpen(await readB64(fs[0]), fs[0].name, "PDF cargado ✔ (con Guardar podrás reemplazar el original)"); });
      return; }
    fileHandle=null; handleChosenFiles(fs);
  }catch(err){ if(err&&err.name==="AbortError")return; $("file").click(); }
});
$("bClose").onclick=async()=>{ if(cur && !await askConfirm("¿Cerrar el documento? Los cambios que no hayas descargado se perderán."))return; cur=null; curDocId=null; pages=0; page=0; lastToc=[];
  $("infoBox").textContent="Sin documento cargado."; $("bDownload").disabled=true; $("bClose").disabled=true; $("bSave").disabled=true; fileHandle=null; dirty=false; dlVer=0;
  histU=[]; histR=[]; updHist(); clearDownloads(); curSizeKB=0; clearTxt(); wipeViewer("Documento cerrado."); };
$("ptPages").onclick=()=>{ $("ptPages").classList.add("on"); $("ptMarks").classList.remove("on"); $("thumbList").style.display="block"; $("tocList").style.display="none"; };
$("ptMarks").onclick=()=>{ $("ptMarks").classList.add("on"); $("ptPages").classList.remove("on"); $("thumbList").style.display="none"; $("tocList").style.display="block"; };
$("qpDel").onclick=()=>runQ(async()=>{ await need(); if(pages<=1)throw new Error("Es la única página");
  const j=await call("/api/delete_pages",{pdf:cur,pages:String(page+1)});
  await adopt(j,curName,true); status("Esta página fue borrada ✔ (solo esa hoja)"); });
$("qpRotL").onclick=()=>runQ(async()=>{ await need();
  const j=await call("/api/rotate",{pdf:cur,pages:String(page+1),degrees:-90});
  await adopt(j,curName,true); status("Página girada a la izquierda ✔"); });
$("qpRotR").onclick=()=>runQ(async()=>{ await need();
  const j=await call("/api/rotate",{pdf:cur,pages:String(page+1),degrees:90});
  await adopt(j,curName,true); status("Página girada a la derecha ✔"); });
$("qpExt").onclick=()=>runQ(async()=>{ await need();
  let j=await call("/api/extract",{pdf:cur,pages:String(page+1)});
  if(!j.pdf && j.doc_id){ j=await call("/api/fetch_doc",{doc_id:j.doc_id}); }
  saveB64(j.pdf,"pagina_"+(page+1)+".pdf"); status("Página "+(page+1)+" lista para descargar ✔"); });
let insMode="after", insTarget=0;
$("qpIns").onclick=()=>{ if(!cur&&!curDocId){status("Primero abre un PDF.",false); return;} $("insPage").value=page+1; $("insTotal").textContent="(el documento tiene "+pages+")"; $("insDlg").style.display="flex"; };
$("insCancel").onclick=()=>{ $("insDlg").style.display="none"; };
function insGo(mode){ const n=parseInt($("insPage").value||"0",10);
  if(!(n>=1&&n<=pages)){ status("Esa página no existe: escribe un número entre 1 y "+pages+".",false); return; }
  insMode=mode; insTarget=n-1; $("insDlg").style.display="none"; $("qpInsFile").click(); }
$("insBefore").onclick=()=>insGo("before");
$("insAfter").onclick=()=>insGo("after");
$("qpInsFile").addEventListener("change",async e=>{ const f=e.target.files[0]; if(!f)return;
  run(async()=>{ const other=await readB64(f);
    const at=(insMode==="before")?insTarget-1:insTarget;
    const j=await callLong("/api/insert_pdf",{pdf:cur,other,at},"Insertar el PDF");
    await adopt(j,curName,true);
    status(j.inserted+" página(s) insertadas "+(insMode==="before"?"antes":"después")+" de la página "+(insTarget+1)+" ✔"); });
  e.target.value=""; });
const viewer=$("pageScroll");
let wzT=null, wzPend=null;
$("pageScroll").addEventListener("wheel",e=>{ if(!e.ctrlKey||(!cur&&!curDocId))return; e.preventDefault();
  wzPend=(wzPend==null?zoom:wzPend)*(e.deltaY<0?1.12:0.89);
  wzPend=Math.max(0.3,Math.min(3.5,wzPend));
  if(wzT)clearTimeout(wzT);
  wzT=setTimeout(async()=>{ zoom=wzPend; wzPend=null; await renderAll(); gotoPage(page,false); },150);
},{passive:false});
viewer.addEventListener("dragover",e=>e.preventDefault());
viewer.addEventListener("drop",e=>{ e.preventDefault(); const fs=[...e.dataTransfer.files]; if(!fs.length)return;
  if(fs.length===1 && !(cur||curDocId)){ const f=fs[0];
    const item=e.dataTransfer.items&&e.dataTransfer.items[0];
    if(item&&item.getAsFileSystemHandle){ item.getAsFileSystemHandle().then(h=>{ fileHandle=(h&&h.kind==="file")?h:null; }).catch(()=>{ fileHandle=null; }); }
    else fileHandle=null;
    run(async()=>{ await tryOpen(await readB64(f), f.name, "PDF cargado ✔"); }); return; }
  fileHandle=null; handleChosenFiles(fs); });
async function doUndo(){ if(pendingStrokes()){ drawStrokes[drawPageNow].pop(); drawPaint(); updHist(); status("Último trazo deshecho ✏️ (ese trazo aún no se había aplicado al PDF)"); return; }
  if(!histU.length){ status("No hay cambios que deshacer."); return; }
  const s=histU.pop(); const j=await call("/api/fetch_doc",{doc_id:s.doc_id});
  histR.push({doc_id:curDocId,name:curName,page}); histJump=true;
  await adopt(j,s.name,true); page=Math.max(0,Math.min(pages-1,s.page)); gotoPage(page,false); syncLabel();
  histJump=false; updHist(); status("Cambio deshecho ↩ (con Rehacer lo recuperas)"); }
async function doRedo(){ if(!histR.length){ status("No hay cambios que rehacer."); return; }
  const s=histR.pop(); const j=await call("/api/fetch_doc",{doc_id:s.doc_id});
  histU.push({doc_id:curDocId,name:curName,page}); histJump=true;
  await adopt(j,s.name,true); page=Math.max(0,Math.min(pages-1,s.page)); gotoPage(page,false); syncLabel();
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
  if(!cur && !curDocId) return true;
  return askConfirm("Ya hay un documento abierto ("+curName+").\n\nSi continúas, ese documento se cerrará y perderás los cambios que NO hayas descargado.\n\n¿Cerrar el actual y continuar?");
}
window.addEventListener("beforeunload",e=>{ if((cur||curDocId)&&dirty){ e.preventDefault(); e.returnValue=""; } });
function clearHighlight(){ const h=$("hlBox"); if(h)h.remove(); }
function closeEditBar(){ $("editBar").style.display="none"; clearHighlight(); closeInline(); }
$("pagesBox").appendChild($("editBar"));
let inlineInp=null;
function closeInline(){ if(inlineInp){ inlineInp.remove(); inlineInp=null; } }
function showInlineEdit(im,j){ closeInline();
  const sx=im.offsetWidth/j.page_w, sy=im.offsetHeight/j.page_h;
  const inp=document.createElement("input"); inp.id="inlineInput"; inp.type="text"; inp.value=j.text;
  inp.style.left=(im.offsetLeft+j.bbox[0]*sx-2)+"px"; inp.style.top=(im.offsetTop+j.bbox[1]*sy-2)+"px";
  inp.style.width=Math.max((j.bbox[2]-j.bbox[0])*sx+6, Math.min(430, im.offsetWidth*0.62))+"px";
  inp.style.height=Math.max((j.bbox[3]-j.bbox[1])*sy+4, 20)+"px";
  inp.style.fontSize=Math.max(11, j.size*sy)+"px"; inp.style.color=rgbHex(j.color);
  inp.style.fontFamily=(j.font&&/times|roman|tiro/i.test(j.font))?"'Times New Roman',serif":((j.font&&/cour/i.test(j.font))?"'Courier New',monospace":"Arial,Helvetica,sans-serif");
  if(j.bold)inp.style.fontWeight="700"; if(j.italic)inp.style.fontStyle="italic";
  inp.addEventListener("keydown",e=>{ e.stopPropagation(); if(e.key==="Enter")$("editOk").click(); if(e.key==="Escape")$("editCancel").click(); });
  inp.addEventListener("keyup",e=>e.stopPropagation());
  inp.addEventListener("click",e=>e.stopPropagation());
  $("pagesBox").appendChild(inp); inlineInp=inp;
  const bar=$("editBar"); bar.style.display="flex";
  let bx=im.offsetLeft+j.bbox[0]*sx, by=im.offsetTop+j.bbox[3]*sy+8;
  const bw=bar.offsetWidth||560;
  const maxX=im.offsetLeft+im.offsetWidth-bw; if(bx>maxX)bx=Math.max(im.offsetLeft,maxX);
  bar.style.left=bx+"px"; bar.style.top=by+"px";
  inp.focus(); inp.select(); }
$("bEditMode").onclick=async()=>{ if(!hasDoc()){ await askInfo("Primero abre un PDF (pestaña «Archivo» → «Abrir PDF»).\n\nLa edición directa trabaja sobre la página de un documento abierto."); return; }
  editMode=!editMode; $("bEditMode").classList.toggle("activo",editMode); $("pagesBox").classList.toggle("editing",editMode);
  document.querySelectorAll(".cpage").forEach(im=>im.style.cursor=editMode?"text":"");
  if(!editMode){ editSel=null; closeEditBar(); setTool("texto"); clearImgOverlay(); status("Edición directa desactivada."); }
  else status("Edición directa ACTIVADA (tipo Nitro): haz clic sobre cualquier cosa del PDF — texto, líneas ______ o imágenes — para editarla o borrarla.");
  renderAll(); };
async function pickLine(ev,im,i){
  if(editTool!=="texto"||imgState)return;
  const r=im.getBoundingClientRect();
  const fx=(ev.clientX-r.left)/r.width, fy=(ev.clientY-r.top)/r.height;
  run(async()=>{ const j=await call("/api/object_at",{pdf:cur,page:i,fx,fy,password:docPw});
    if(j.kind!=="text"){ if(j.kind){ objSel={page:i,rect:j.rect,kind:j.kind}; drawObjHl(im,j); openObjDlg(j); } else status("Ahí no hay nada editable: ni texto, ni líneas, ni imágenes (si es un escaneo, usa OCR).",false); return; }
    editSel={page:i,bbox:j.bbox,origin:j.origin,size:j.size,font:j.font,color:j.color,page_w:j.page_w,page_h:j.page_h,dir:j.dir||[1,0]};
    $("edSize").value=Math.round(j.size*10)/10; $("edColor").value=rgbHex(j.color);
    $("edB").classList.toggle("on",!!j.bold); $("edI").classList.toggle("on",!!j.italic);
    $("edU").classList.remove("on"); $("edS").classList.remove("on");
    $("edFont").value=""; $("edBgOn").checked=false;
    clearHighlight();
    const hl=document.createElement("div"); hl.id="hlBox";
    const sx=im.offsetWidth/j.page_w, sy=im.offsetHeight/j.page_h;
    hl.style.left=(im.offsetLeft+j.bbox[0]*sx)+"px"; hl.style.top=(im.offsetTop+j.bbox[1]*sy)+"px";
    hl.style.width=((j.bbox[2]-j.bbox[0])*sx)+"px"; hl.style.height=((j.bbox[3]-j.bbox[1])*sy)+"px";
    $("pagesBox").appendChild(hl);
    showInlineEdit(im,j);
    status(j.blank?"Es una línea de relleno (______): deja el texto VACÍO y pulsa ✔ Aplicar para borrarla.":"Editando EN el documento: escribe sobre la línea (el cursor ya parpadea ahí) y pulsa ✔ Aplicar; la barra de formato está junto a la línea."); });
}
$("editCancel").onclick=()=>{ editSel=null; closeEditBar(); status("Edición cancelada."); };
$("editInput").addEventListener("keydown",e=>{ if(e.key==="Enter")$("editOk").click(); if(e.key==="Escape")$("editCancel").click(); });
$("editOk").onclick=()=>run(async()=>{ if(!editSel)throw new Error("Primero haz clic en una línea del PDF");
  const j=await call("/api/edit_line",{pdf:cur,page:editSel.page,bbox:editSel.bbox,origin:editSel.origin,dir:editSel.dir,
    size:parseFloat($("edSize").value)||editSel.size,font:editSel.font,family:$("edFont").value||null,
    bold:$("edB").classList.contains("on"),italic:$("edI").classList.contains("on"),
    underline:$("edU").classList.contains("on"),strike:$("edS").classList.contains("on"),
    color:hexRgb($("edColor").value),bg:$("edBgOn").checked?hexRgb($("edBg").value):null,
    text:(inlineInp?inlineInp.value:$("editInput").value),password:docPw});
  editSel=null; closeEditBar();
  await adopt(j,"editado.pdf",true);
  status("Línea editada sobre el PDF ✔ (el documento sigue abierto, ya corregido)"); });

let objSel=null;
function drawObjHl(im,j){ clearHighlight(); const hl=document.createElement("div"); hl.id="hlBox";
  const sx=im.offsetWidth/j.page_w, sy=im.offsetHeight/j.page_h;
  hl.style.left=(im.offsetLeft+j.rect[0]*sx)+"px"; hl.style.top=(im.offsetTop+j.rect[1]*sy)+"px";
  hl.style.width=Math.max(6,(j.rect[2]-j.rect[0])*sx)+"px"; hl.style.height=Math.max(4,(j.rect[3]-j.rect[1])*sy)+"px";
  $("pagesBox").appendChild(hl); }
function openObjDlg(j){ const T={linea:"Línea seleccionada",dibujo:"Dibujo seleccionado",imagen:"Imagen seleccionada"};
  const D={linea:"Es una línea DIBUJADA del documento (como las de ______ para rellenar a mano). Puedes ESCRIBIR sobre ella, cambiar su color y grosor, o borrarla sin tocar nada más.",
           dibujo:"Es una forma o dibujo del documento (un recuadro, una tabla, una figura). Puedes borrarlo sin tocar el texto.",
           imagen:"Es una imagen del documento. Puedes borrarla; el texto queda intacto."};
  $("objTitle").textContent=T[j.kind]||"Objeto seleccionado"; $("objDesc").textContent=D[j.kind]||"";
  const canStyle=(j.kind==="linea"||j.kind==="dibujo");
  $("objOpts").style.display=canStyle?"flex":"none";
  $("objWrite").style.display=(j.kind==="linea")?"block":"none";
  if(j.kind==="linea")$("objText").value="";
  if(canStyle){ $("objColor").value=rgbHex(j.color||[0,0,0]); $("objWidth").value=j.width||1; }
  $("objDlg").style.display="flex"; }
$("objCancel").onclick=()=>{ $("objDlg").style.display="none"; objSel=null; clearHighlight(); };
$("objDel").onclick=()=>run(async()=>{ if(!objSel)throw new Error("No hay objeto seleccionado");
  const j=await call("/api/delete_object",{pdf:cur,page:objSel.page,rect:objSel.rect,kind:objSel.kind,password:docPw});
  $("objDlg").style.display="none"; objSel=null; clearHighlight();
  await adopt(j,"editado.pdf",true); status("Objeto borrado del documento ✔ (con Deshacer lo recuperas)"); });
$("objWriteBtn").onclick=()=>run(async()=>{ if(!objSel)throw new Error("No hay línea seleccionada");
  const t=$("objText").value.trim(); if(!t)throw new Error("Escribe primero el texto que va sobre la línea");
  const j=await call("/api/write_on_line",{pdf:cur,page:objSel.page,rect:objSel.rect,text:t,size:parseFloat($("objTextSize").value)||11,color:hexRgb($("objColor").value),password:docPw});
  $("objDlg").style.display="none"; objSel=null; clearHighlight();
  await adopt(j,"editado.pdf",true); status("Texto escrito sobre la línea ✔ (la línea queda debajo, como en el formulario)"); });
$("objApply").onclick=()=>run(async()=>{ if(!objSel)throw new Error("No hay objeto seleccionado");
  const j=await call("/api/restyle_object",{pdf:cur,page:objSel.page,rect:objSel.rect,kind:objSel.kind,color:hexRgb($("objColor").value),width:parseFloat($("objWidth").value)||1,password:docPw});
  $("objDlg").style.display="none"; objSel=null; clearHighlight();
  await adopt(j,"editado.pdf",true); status("Objeto actualizado ✔ (color y grosor nuevos, en el mismo sitio)"); });

// ===== Editor 1.17: formato, imagen sobre la pagina, lapiz/borrador, vista en grande =====
function rgbHex(c){ if(!c)return "#000000"; const h=v=>Math.max(0,Math.min(255,Math.round(v*255))).toString(16).padStart(2,"0"); return "#"+h(c[0])+h(c[1])+h(c[2]); }
function hexRgb(hx){ const n=parseInt(hx.slice(1),16); return [((n>>16)&255)/255,((n>>8)&255)/255,(n&255)/255]; }
["edB","edI","edU","edS"].forEach(id=>{ $(id).onclick=()=>$(id).classList.toggle("on"); });
let editTool="texto";
function setTool(t){ editTool=t;
  [["bToolPen","lapiz"],["bToolHi","resaltar"],["bToolErase","borrador"]].forEach(([id,v])=>{ const b=$(id); if(b)b.classList.toggle("activo",t===v); });
  drawAttach(); }
async function ensureEdit(){ if(!hasDoc()){ await askInfo("Primero abre un PDF (pestaña «Archivo» → «Abrir PDF»).\n\nEstas herramientas trabajan sobre la página de un documento: sin un PDF abierto no hay dónde dibujar ni editar."); return false; } if(!editMode)$("bEditMode").click(); return true; }
$("bToolPen").onclick=async()=>{ if(await ensureEdit()){ setTool(editTool==="lapiz"?"texto":"lapiz"); status(editTool==="lapiz"?"Lápiz ACTIVADO: dibuja sobre la página actual y al terminar pulsa «✔ Aplicar trazos».":"Lápiz desactivado."); } };
$("bToolHi").onclick=async()=>{ if(await ensureEdit()){ setTool(editTool==="resaltar"?"texto":"resaltar"); status(editTool==="resaltar"?"Resaltador ACTIVADO: pasa el puntero sobre lo que quieras resaltar y pulsa «✔ Aplicar trazos».":"Resaltador desactivado."); } };
$("bToolErase").onclick=async()=>{ if(await ensureEdit()){ setTool(editTool==="borrador"?"texto":"borrador"); status(editTool==="borrador"?"Borrador ACTIVADO: arrastra sobre los trazos y se borra solo la parte que tocas, como un borrador de verdad (antes de aplicarlos).":"Borrador desactivado."); } };
let drawStrokes={}, drawCanvas=null, drawPageNow=-1, drawCur=null;
function drawAttach(){
  const old=document.getElementById("drawCv");
  const active=editMode&&(editTool==="lapiz"||editTool==="resaltar"||editTool==="borrador")&&(cur||curDocId);
  if(!active){ if(old)old.remove(); const _rg0=document.getElementById("eraseRing"); if(_rg0)_rg0.remove(); drawCanvas=null; drawPageNow=-1; return; }
  const wrap=document.querySelector('.pgwrap[data-pg="'+page+'"]');
  if(!wrap)return;
  if(old&&old.parentElement===wrap&&drawPageNow===page){ drawPaint(); return; }
  if(old)old.remove();
  const cv=document.createElement("canvas"); cv.id="drawCv";
  cv.style.cssText="position:absolute;inset:0;width:100%;height:100%;z-index:5;touch-action:none;cursor:"+(editTool==="borrador"?"none":"crosshair");
  const _rgOld=document.getElementById("eraseRing"); if(_rgOld)_rgOld.remove();
  if(editTool==="borrador"){ const rg=document.createElement("div"); rg.id="eraseRing"; wrap.appendChild(rg); }
  cv.width=wrap.clientWidth; cv.height=wrap.clientHeight;
  wrap.appendChild(cv); drawCanvas=cv; drawPageNow=page;
  cv.addEventListener("pointerdown",drawDown); cv.addEventListener("pointermove",drawMove);
  cv.addEventListener("pointerup",drawUp); cv.addEventListener("pointercancel",drawUp);
  drawPaint(); }
function drawScale(){ const sz=pageSizes[drawPageNow]||pageSizes[0]||[595,842]; const r=drawCanvas.getBoundingClientRect(); return {sx:sz[0]/r.width, sy:sz[1]/r.height}; }
function drawEvtPt(e){ const r=drawCanvas.getBoundingClientRect(); const sc=drawScale(); return [(e.clientX-r.left)*sc.sx,(e.clientY-r.top)*sc.sy]; }
function drawPaint(){ if(!drawCanvas)return; const ctx=drawCanvas.getContext("2d"); const sc=drawScale();
  ctx.clearRect(0,0,drawCanvas.width,drawCanvas.height);
  (drawStrokes[drawPageNow]||[]).forEach(st=>{ ctx.save(); ctx.globalAlpha=st.opacity; ctx.strokeStyle=st.color; ctx.fillStyle=st.color; ctx.lineWidth=st.width/sc.sx; ctx.lineCap="round"; ctx.lineJoin="round";
    if(st.pts.length===1){ ctx.beginPath(); ctx.arc(st.pts[0][0]/sc.sx,st.pts[0][1]/sc.sy,Math.max(1,(st.width/sc.sx)/2),0,7); ctx.fill(); }
    else { ctx.beginPath(); st.pts.forEach((p,k)=>{ const x=p[0]/sc.sx, y=p[1]/sc.sy; if(k===0)ctx.moveTo(x,y); else ctx.lineTo(x,y); }); ctx.stroke(); }
    ctx.restore(); }); }
let eraseOn=false, eraseLast=null;
function drawDown(e){ if(!drawCanvas)return; e.preventDefault(); try{drawCanvas.setPointerCapture(e.pointerId);}catch(_){ }
  const p=drawEvtPt(e);
  if(editTool==="borrador"){ eraseOn=true; eraseLast=p; eraseSeg(p,p); moveRing(e); return; }
  const hi=editTool==="resaltar";
  drawCur={pts:[p],color:hi?"#ffeb3b":$("drawColor").value,width:hi?14:parseFloat($("drawWidth").value||"3"),opacity:hi?0.35:1};
  (drawStrokes[drawPageNow]=drawStrokes[drawPageNow]||[]).push(drawCur); drawPaint(); }
function drawMove(e){ if(editTool==="borrador"){ moveRing(e); if(eraseOn){ const p=drawEvtPt(e); eraseSeg(eraseLast||p,p); eraseLast=p; } return; }
  if(!drawCur)return; const p=drawEvtPt(e); const last=drawCur.pts[drawCur.pts.length-1];
  if(Math.hypot(p[0]-last[0],p[1]-last[1])>=1.2){ drawCur.pts.push(p); drawPaint(); } }
function drawUp(){ if(drawCur){ drawCur=null; updHist(); } if(eraseOn){ eraseOn=false; eraseLast=null; } const rg=document.getElementById("eraseRing"); if(rg)rg.style.display="none"; }
function eraseRadiusPt(){ const sc=drawScale(); return Math.max(7,parseFloat($("drawWidth").value||"3")*2.2)*sc.sx; }
function eraseSeg(a,b){ const arr=drawStrokes[drawPageNow]||[]; if(!arr.length)return; const R=eraseRadiusPt(); let changed=false;
  const dSeg=p=>{ const vx=b[0]-a[0],vy=b[1]-a[1]; const L2=vx*vx+vy*vy||1; let t=((p[0]-a[0])*vx+(p[1]-a[1])*vy)/L2; t=Math.max(0,Math.min(1,t)); return Math.hypot(p[0]-(a[0]+t*vx),p[1]-(a[1]+t*vy)); };
  const out=[];
  for(const st of arr){ const rr=R+st.width/2; let run=[];
    const flush=()=>{ if(run.length>=2)out.push(Object.assign({},st,{pts:run})); else if(run.length===1&&st.pts.length===1)out.push(Object.assign({},st,{pts:run})); run=[]; };
    for(const p of st.pts){ if(dSeg(p)<=rr){ flush(); changed=true; } else run.push(p); }
    flush(); }
  if(changed){ drawStrokes[drawPageNow]=out; drawPaint(); updHist(); } }
function moveRing(e){ const rg=document.getElementById("eraseRing"); if(!rg||!drawCanvas)return; const wr=drawCanvas.parentElement.getBoundingClientRect(); const d=Math.max(14,parseFloat($("drawWidth").value||"3")*4.4);
  rg.style.display="block"; rg.style.width=d+"px"; rg.style.height=d+"px"; rg.style.left=(e.clientX-wr.left-d/2)+"px"; rg.style.top=(e.clientY-wr.top-d/2)+"px"; }
$("bDrawClear").onclick=()=>{ if(drawPageNow>=0)drawStrokes[drawPageNow]=[]; drawPaint(); updHist(); status("Trazos de esta página descartados (el PDF no se tocó)."); };
$("bDrawApply").onclick=()=>run(async()=>{ await need();
  const pags=Object.keys(drawStrokes).filter(k=>drawStrokes[k].length);
  if(!pags.length)throw new Error("Todavía no dibujaste nada: activa el lápiz o el resaltador y dibuja sobre la página.");
  for(const k of pags){ const j=await call("/api/draw_strokes",{pdf:cur,page:+k,strokes:drawStrokes[k],password:docPw}); await adopt(j,curName,true); }
  drawStrokes={}; const cv=document.getElementById("drawCv"); if(cv)cv.remove(); const _rgA=document.getElementById("eraseRing"); if(_rgA)_rgA.remove(); drawCanvas=null; drawPageNow=-1; updHist();
  status("Trazos aplicados sobre el PDF ✔"); });
let imgState=null, imgDrag=null, imgReplace=false;
function clearImgOverlay(){ const o=document.getElementById("imgOv"); if(o)o.remove(); imgState=null; const b=$("imgBar"); if(b)b.style.display="none"; }
function imgHF(){ const sz=pageSizes[imgState.page]||pageSizes[0]||[595,842]; return imgState.W*sz[0]*(imgState.ih/Math.max(1,imgState.iw))/sz[1]; }
function imgPaintOv(ov){ if(!imgState)return; ov=ov||document.getElementById("imgOv"); if(!ov)return;
  ov.style.left=(imgState.L*100)+"%"; ov.style.top=(imgState.T*100)+"%"; ov.style.width=(imgState.W*100)+"%"; ov.style.height=(imgHF()*100)+"%";
  ov.style.transform="rotate("+imgState.angle+"deg)";
  const im=ov.querySelector("img"); if(im)im.style.filter="brightness("+imgState.bright+") contrast("+imgState.contrast+")"; }
function imgAttach(){ const old=document.getElementById("imgOv");
  if(!imgState){ if(old)old.remove(); return; }
  const wrap=document.querySelector('.pgwrap[data-pg="'+imgState.page+'"]');
  if(!wrap)return;
  if(old&&old.parentElement===wrap){ imgPaintOv(old); return; }
  if(old)old.remove();
  const ov=document.createElement("div"); ov.id="imgOv";
  ov.style.cssText="position:absolute;z-index:6;border:1.5px dashed var(--acc);cursor:move;touch-action:none";
  const im=document.createElement("img"); im.src=imgState.url; im.style.cssText="width:100%;height:100%;display:block;pointer-events:none";
  const hd=document.createElement("div"); hd.style.cssText="position:absolute;right:-9px;bottom:-9px;width:18px;height:18px;border-radius:50%;background:var(--acc);border:2px solid #fff;cursor:nwse-resize;z-index:2";
  ov.append(im,hd); wrap.appendChild(ov); imgPaintOv(ov);
  ov.addEventListener("pointerdown",e=>{ if(e.target===hd)return; imgDrag={mode:"move",x:e.clientX,y:e.clientY,L:imgState.L,T:imgState.T}; try{ov.setPointerCapture(e.pointerId);}catch(_){ } e.preventDefault(); });
  hd.addEventListener("pointerdown",e=>{ imgDrag={mode:"size",x:e.clientX,W:imgState.W}; try{ov.setPointerCapture(e.pointerId);}catch(_){ } e.stopPropagation(); e.preventDefault(); });
  ov.addEventListener("pointermove",e=>{ if(!imgDrag)return; const r=wrap.getBoundingClientRect();
    if(imgDrag.mode==="move"){ imgState.L=Math.min(0.98,Math.max(0,imgDrag.L+(e.clientX-imgDrag.x)/r.width)); imgState.T=Math.min(0.98,Math.max(0,imgDrag.T+(e.clientY-imgDrag.y)/r.height)); }
    else { imgState.W=Math.min(1,Math.max(0.05,imgDrag.W+(e.clientX-imgDrag.x)/r.width)); $("imSize").value=Math.round(imgState.W*100); }
    imgPaintOv(ov); });
  ov.addEventListener("pointerup",()=>{ imgDrag=null; }); ov.addEventListener("pointercancel",()=>{ imgDrag=null; }); }
$("bImgAdd").onclick=async()=>{ if(!hasDoc()){ await askInfo("Para insertar una imagen primero abre un PDF.\n\nLa imagen se coloca sobre una página del documento: sin un PDF abierto no hay dónde insertarla."); return; } if(!editMode)$("bEditMode").click(); imgReplace=false; $("imgFile").click(); };
$("imRepl").onclick=()=>{ imgReplace=true; $("imgFile").click(); };
$("imgFile").addEventListener("change",async e=>{ const f=e.target.files[0]; e.target.value=""; if(!f)return;
  const url=URL.createObjectURL(f); const probe=new Image();
  probe.onload=async()=>{ const b64=await readB64(f);
    if(imgReplace&&imgState){ imgState.b64=b64; imgState.url=url; imgState.iw=probe.naturalWidth; imgState.ih=probe.naturalHeight; const o=document.getElementById("imgOv"); if(o)o.remove(); imgAttach(); status("Imagen reemplazada: ajusta lo que quieras y pulsa «✔ Aplicar»."); return; }
    imgState={page:page,b64: b64,url:url,iw:probe.naturalWidth,ih:probe.naturalHeight,L:0.35,T:0.35,W:0.3,angle:0,bright:1,contrast:1};
    $("imAng").value=0; $("imSize").value=30; $("imBr").value=100; $("imCt").value=100;
    $("imgBarPg").textContent=page+1; $("imgBar").style.display="flex"; imgAttach();
    status("Imagen colocada sobre la página "+(page+1)+": arrástrala para moverla, tira de la esquina azul para el tamaño y pulsa «✔ Aplicar»."); };
  probe.onerror=()=>{ showErr("Ese archivo no se pudo leer como imagen."); };
  probe.src=url; });
$("imAng").addEventListener("input",e=>{ if(imgState){ imgState.angle=+e.target.value; imgPaintOv(); } });
$("imSize").addEventListener("input",e=>{ if(imgState){ imgState.W=(+e.target.value)/100; imgPaintOv(); } });
$("imBr").addEventListener("input",e=>{ if(imgState){ imgState.bright=(+e.target.value)/100; imgPaintOv(); } });
$("imCt").addEventListener("input",e=>{ if(imgState){ imgState.contrast=(+e.target.value)/100; imgPaintOv(); } });
$("imRot90").onclick=()=>{ if(imgState){ imgState.angle=((imgState.angle+90+180)%360)-180; $("imAng").value=imgState.angle; imgPaintOv(); } };
$("imCancel").onclick=()=>{ clearImgOverlay(); status("Imagen retirada (el PDF no se tocó)."); };
$("imOk").onclick=()=>run(async()=>{ if(!imgState)throw new Error("No hay ninguna imagen por aplicar");
  const sz=pageSizes[imgState.page]||pageSizes[0]||[595,842];
  const wPt=imgState.W*sz[0];
  const cx=(imgState.L+imgState.W/2)*sz[0], cy=(imgState.T+imgHF()/2)*sz[1];
  const pgN=imgState.page+1;
  const j=await call("/api/place_image",{pdf:cur,page:imgState.page,img:imgState.b64,cx:cx,cy:cy,w_pt:wPt,angle:imgState.angle,bright:imgState.bright,contrast:imgState.contrast,password:docPw});
  clearImgOverlay(); await adopt(j,curName,true);
  status("Imagen insertada en la página "+pgN+" ✔"); });
let pvScale=1;
function openPv(src){ $("pvImg").src=src; pvScale=1; $("pvImg").style.width="100%"; $("pvDlg").style.display="flex"; }
$("pvClose").onclick=()=>{ $("pvDlg").style.display="none"; if(document.fullscreenElement)document.exitFullscreen(); };
$("pvIn").onclick=()=>{ pvScale=Math.min(4,pvScale*1.25); $("pvImg").style.width=(pvScale*100)+"%"; };
$("pvOut").onclick=()=>{ pvScale=Math.max(0.3,pvScale/1.25); $("pvImg").style.width=(pvScale*100)+"%"; };
$("pvFull").onclick=()=>{ const d=$("pvDlg"); if(document.fullscreenElement)document.exitFullscreen(); else if(d.requestFullscreen)d.requestFullscreen(); };
async function openPvPage(i){ run(async()=>{ const j=await call("/api/render",{doc_id:curDocId,page:i,zoom:1.5,password:docPw}); openPv("data:image/png;base64,"+j.png); }); }
async function openPvMg(tk){ run(async()=>{ if(tk.k==="cur"){ const j=await call("/api/render",{doc_id:curDocId,page:0,zoom:1.5,password:docPw}); openPv("data:image/png;base64,"+j.png); }
  else { const j=await call("/api/info",{doc_id:tk.it.doc_id,thumb:1,thumbz:1.4}); if(!j.thumb)throw new Error("Ese PDF no dejó ver su primera página"); openPv("data:image/png;base64,"+j.thumb); } }); }
$("bDownload").onclick=downloadCurrent;
$("qpDl").onclick=downloadCurrent;
$("qpSave").onclick=()=>$("bSave").click();
async function fhPerm(h){ try{ return await h.queryPermission({mode:"readwrite"}); }catch(_){ return "prompt"; } }
async function writeOriginal(h){ await ensureBytes(); const w=await h.createWritable(); await w.write(b64ToBlob(cur)); await w.close(); fileHandle=h; dirty=false; status("Cambios guardados en el archivo original ✔ ("+curName+")"); }
$("bSave").onclick=()=>run(async()=>{ await need();
  if(!dirty){ status("Este documento no tiene cambios nuevos por guardar."); return; }
  // 1.19: si Edge ya dio el permiso de escritura al abrir el archivo, Guardar
  // escribe DIRECTO, sin ninguna ventana (ni del programa ni de Edge).
  if(fileHandle && (await fhPerm(fileHandle))==="granted"){ await writeOriginal(fileHandle); return; }
  const canPick=!!window.showSaveFilePicker;
  $("svReplace").disabled=!(fileHandle||canPick);
  $("svNote").textContent=fileHandle?"Edge pedirá su permiso de escritura una sola vez al pulsar «Reemplazar»; después de eso, Guardar será directo y sin ventanas.":(canPick?"Al pulsar «Reemplazar el archivo original» se abrirá el selector de Edge: elige el MISMO archivo para sobrescribirlo. Es la única ventana de Edge en este paso.":"Sin acceso directo al archivo original en este navegador: usa «Guardar como copia nueva».");
  $("svDlg").style.display="flex"; });
$("svCancel").onclick=()=>{ $("svDlg").style.display="none"; };
$("svCopy").onclick=()=>{ $("svDlg").style.display="none"; downloadCurrent(); };
$("svReplace").onclick=()=>run(async()=>{ $("svDlg").style.display="none";
  await ensureBytes();
  let h=fileHandle;
  if(h){ const perm=await h.requestPermission({mode:"readwrite"});
    if(perm!=="granted")throw new Error("No diste permiso para escribir el archivo original"); }
  else{ if(!window.showSaveFilePicker)throw new Error("Este navegador no da acceso al archivo original: usa «Guardar como copia nueva».");
    try{ h=await window.showSaveFilePicker({suggestedName:curName,types:[{description:"PDF",accept:{"application/pdf":[".pdf"]}}]}); }
    catch(_){ status("Reemplazo cancelado: no se eligió ningún archivo."); return; } }
  await writeOriginal(h); });
$("pwOkBtn").onclick=()=>{ $("pwDlg").style.display="none"; };
let ciItems=[], ciDragI=-1;
function renderCi(){ const box=$("ciList"); box.innerHTML="";
  if(!ciItems.length){ box.innerHTML="<div style='color:var(--mut);font-size:13.5px'>Aún no añades imágenes. Pulsa «Añadir imágenes…» y elige las fotos o escaneos.</div>"; return; }
  ciItems.forEach((it,i)=>{ const d=document.createElement("div"); d.className="mgcard"; d.draggable=true; d.title="Arrástrame para cambiar el orden";
    const grip=document.createElement("span"); grip.textContent="⠿"; grip.style.cssText="color:var(--mut);cursor:grab;font-size:15px;flex:none";
    const im=document.createElement("img"); im.src=it.url; im.className="mgthumb";
    const num=document.createElement("span"); num.className="mgnum"; num.textContent=i+1;
    const nm=document.createElement("span"); nm.className="mgname"; nm.textContent=it.name; nm.title=it.name;
    const pg=document.createElement("span"); pg.className="mgpg"; pg.textContent=fmtSize(it.size/1024);
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
  const j=await callLong("/api/images_to_pdf",{images:arr},"Crear el PDF desde imágenes"); await adopt(j,"desde_imagenes.pdf");
  status("PDF creado desde "+arr.length+" imagen(es) ✔"); });
$("bTxtPdf").onclick=()=>run(async()=>{ if(!await confirmarReemplazo())return; const t=$("txtBody").value; if(!t.trim())throw new Error("Escribe un texto");
  const j=await call("/api/text_to_pdf",{text:t,title:$("txtTitle").value}); await adopt(j,"desde_texto.pdf"); status("PDF creado desde texto ✔"); });
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
  $("pgSecBoard").style.display=kind==="split"?"none":"block"; pgSel.clear(); pgBoardDoc=null; $("pgDlg").querySelector(".box").classList.remove("wide"); $("pgBoard").style.display="none";
  $("pgBoard").style.display="none"; $("pgBoard").dataset.done=""; $("pgBoardInfo").textContent="";
  $("pgDlg").style.display="flex"; }
$("bExtract").onclick=()=>run(async()=>{ await need(); openPgDlg("extract"); });
$("bSplit").onclick=()=>run(async()=>{ await need(); openPgDlg("split"); });
$("bDel").onclick=()=>run(async()=>{ await need(); openPgDlg("del"); });
$("pgCancel").onclick=()=>{ $("pgDlg").style.display="none"; };
document.querySelectorAll("#pgDlg .pgsec input[type=text], #pgDlg .pgsec input[type=number]").forEach(inp=>{
  inp.addEventListener("focus",()=>{ const sec=inp.closest(".pgsec"); const r=sec&&sec.querySelector('input[type="radio"]'); if(r)r.checked=true; }); });
let pgSel=new Set(), pgBoardDoc=null;
function pgMarkChip(chip,i){ const on=pgSel.has(i); const col=pgKind==="del"?"#b91c1c":"var(--az)";
  chip.style.borderColor=on?col:"var(--line)"; chip.style.background=on?(pgKind==="del"?"#fdf0f0":"#eef4ff"):"#fff"; }
function pgPaintSel(){ $("pgBoardInfo").textContent=pgSel.size?("Seleccionadas: "+[...pgSel].sort((a,b)=>a-b).map(x=>x+1).join(", ")):("Toca las páginas que quieras "+(pgKind==="del"?"borrar":"extraer")+"."); }
$("pgBoardBtn").onclick=async()=>{ const box=$("pgBoard");
  if(box.style.display!=="none"){ box.style.display="none"; $("pgDlg").querySelector(".box").classList.remove("wide"); return; }
  box.style.display="block"; $("pgDlg").querySelector(".box").classList.add("wide");
  if(pgBoardDoc===curDocId && box.dataset.done==="1"){ pgPaintSel(); return; }
  box.dataset.done=""; box.innerHTML="<div style='color:var(--mut);font-size:13px'>Cargando miniaturas…</div>";
  const pc=pages<=8?4:pages<=15?5:pages<=24?6:pages<=40?7:pages<=60?8:pages<=90?9:10;
  const grid=document.createElement("div"); grid.className="pggrid"; grid.style.gridTemplateColumns="repeat("+pc+",1fr)"; grid.style.gridAutoRows="minmax(104px,1fr)";
  const chips=[];
  for(let i=0;i<pages;i++){ const chip=document.createElement("div"); chip.dataset.pg=i;
    chip.className="pgchip";
    chip.innerHTML="<div class='pgbImg' style='flex:1;min-height:0;width:100%;display:flex;align-items:center;justify-content:center;color:var(--mut);font-size:12px'>…</div><div style='font-size:12px;font-weight:700;margin-top:3px'>Pág. "+(i+1)+"</div>";
    chip.onclick=()=>{ if(pgSel.has(i))pgSel.delete(i); else pgSel.add(i); pgMarkChip(chip,i); pgPaintSel(); };
    const pvb=document.createElement("button"); pvb.textContent="🔍"; pvb.title="Ver esta página en grande";
    pvb.style.cssText="position:absolute;top:3px;right:3px;border:1px solid var(--line);background:#fff;border-radius:6px;cursor:pointer;font-size:12px;padding:1px 5px;z-index:2";
    pvb.onclick=e=>{ e.stopPropagation(); openPvPage(i); };
    chip.style.position="relative"; chip.appendChild(pvb);
    chips.push(chip); grid.append(chip); }
  box.innerHTML=""; box.append(grid);
  for(let k=0;k<chips.length;k+=6){ await Promise.all(chips.slice(k,k+6).map(async chip=>{ const i=+chip.dataset.pg;
    try{ const j=await call("/api/render",{doc_id:curDocId,page:i,zoom:0.16,password:docPw});
      chip.querySelector(".pgbImg").innerHTML="<img src='data:image/png;base64,"+j.png+"' style='max-width:100%;max-height:100%;border-radius:4px'>"; }catch(e){ } })); }
  chips.forEach(c=>pgMarkChip(c,+c.dataset.pg));
  pgBoardDoc=curDocId; box.dataset.done="1"; pgPaintSel(); };
$("pgOk").onclick=()=>run(async()=>{
  const mode=document.querySelector('input[name="pgMode"]:checked').value;
  if(pgKind==="split"){
    if(mode==="fixed"){ const n=parseInt($("pgN").value||"1",10); if(!(n>=1))throw new Error("El tamaño de parte debe ser 1 o más");
      $("pgDlg").style.display="none";
      const j=await callLong("/api/split",{pdf:cur,mode:"fixed",n},"Dividir el PDF");
      saveB64(j.zip,"dividido.zip","application/zip"); status("PDF dividido en "+j.parts+" parte(s) ✔ (ZIP descargado)"); }
    else { const spec=$("pgRanges").value.trim(); if(!spec)throw new Error("Escribe los rangos, p. ej. 1-3, 5-6");
      $("pgDlg").style.display="none";
      const j=await callLong("/api/split",{pdf:cur,mode:"ranges",spec},"Dividir el PDF");
      saveB64(j.zip,"dividido.zip","application/zip"); status("PDF dividido en "+j.parts+" parte(s) ✔ (ZIP descargado)"); }
    return; }
  let spec="";
  if(pgSel.size){ spec=[...pgSel].sort((a,b)=>a-b).map(x=>x+1).join(","); }
  else if(mode==="range"){ const a=parseInt($("pgFrom").value||"1",10), b=parseInt($("pgTo").value||"1",10);
    if(!(a>=1&&b>=a&&b<=pages))throw new Error("Rango no válido: debe ir del 1 al "+pages+" y «desde» no puede ser mayor que «hasta»");
    spec=a+"-"+b; }
  else { spec=$("pgList").value.trim(); if(!spec)throw new Error("Escribe las páginas, p. ej. 2, 5, 7"); }
  $("pgDlg").style.display="none";
  if(pgKind==="extract"){ const j=await call("/api/extract",{pdf:cur,pages:spec});
    await adopt(j,"extraido.pdf"); status("Páginas extraídas ✔ (quedó abierto el PDF extraído)"); }
  else { const j=await call("/api/delete_pages",{pdf:cur,pages:spec});
    await adopt(j,curName,true); status("Páginas borradas ✔"); }
});
$("bRotR").onclick=()=>openRotDlg(90);
$("bRotL").onclick=()=>openRotDlg(-90);
let mgItems=[]; let mgDragI=-1; let mgExcludeCur=false;
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
$("bMerge").onclick=()=>{ mgExcludeCur=false; mgItems=[]; mgSeq=null; renderMg(); mgShowBoard(); $("mgDlg").style.display="flex"; };
$("mgCancel").onclick=()=>{ $("mgDlg").style.display="none"; mgExcludeCur=false; };
$("mgFiles").addEventListener("change",async e=>{ const fs=[...e.target.files]; e.target.value=""; await mgAddFiles(fs); });
let mgSeq=null, mgBoardUsed=false, mgDragSi=-1;
let mgCurThumb=null, mgCurThumbDoc=null, mgCurThumbBusy=false;
function mgBuildSeq(){ const pos=document.querySelector('input[name="mgPos"]:checked').value;
  const files=mgItems.map(it=>({k:"f",it}));
  mgSeq=((cur||curDocId)&&!mgExcludeCur)?(pos==="start"?[{k:"cur"},...files]:[...files,{k:"cur"}]):files; }
function renderMgBoard(){ const box=$("mgBoard"); if(!mgSeq)mgBuildSeq(); box.innerHTML="";
  const hint=document.createElement("div"); hint.style.cssText="font-size:12.5px;color:var(--mut);margin-bottom:7px";
  hint.textContent="Arrastra los bloques para dejar el orden exacto en que se unirán (el azul es el documento que ya tienes abierto).";
  const n=mgSeq.length;
  const cols=Math.max(1,Math.min(6,Math.round(Math.sqrt(n*1.9))));
  const rows=Math.max(1,Math.ceil(n/cols));
  const fz="12px", iz="17px", bz="18px";
  const grid=document.createElement("div"); grid.className="mggrid";
  grid.style.cssText="grid-template-columns:repeat("+cols+",1fr);grid-auto-rows:minmax(158px,1fr)";
  mgSeq.forEach((tk,si)=>{ const card=document.createElement("div"); card.draggable=true;
    card.className="mgcard";
    card.style.cssText="border:1.5px solid "+(tk.k==="cur"?"var(--az)":"var(--line)")+";background:"+(tk.k==="cur"?"#eef4ff":"#fff");
    const nm=tk.k==="cur"?(curName||"Documento actual"):tk.it.name;
    const pg=tk.k==="cur"?pages:tk.it.pages;
    const th=tk.k==="cur"?mgCurThumb:tk.it.thumb;
    const vis=th?("<img src='data:image/png;base64,"+th+"' style='max-height:60px;max-width:92%;border-radius:4px;box-shadow:0 1px 5px rgba(15,23,42,.25)'>"):("<div style='font-size:"+iz+"'>"+(tk.k==="cur"?"📘":"📕")+"</div>");
    card.innerHTML="<div style='height:62px;display:flex;align-items:center;justify-content:center'>"+vis+"</div><div style='font-size:"+fz+";font-weight:600;word-break:break-all;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden'>"+String(nm).replace(/</g,"&lt;")+"</div><div style='font-size:11px;color:var(--mut);margin-top:3px'>"+(pg?pg+" págs":"")+"</div><div style='margin-top:5px'><span style='background:var(--az);color:#fff;border-radius:50%;display:inline-flex;width:"+bz+";height:"+bz+";align-items:center;justify-content:center;font-size:11px;font-weight:700'>"+(si+1)+"</span></div>";
    const pvb=document.createElement("button"); pvb.textContent="🔍"; pvb.title="Ver la primera página en grande";
    pvb.style.cssText="position:absolute;top:4px;right:4px;border:1px solid var(--line);background:#fff;border-radius:6px;cursor:pointer;font-size:12px;padding:1px 5px;z-index:2";
    pvb.onclick=e=>{ e.stopPropagation(); openPvMg(tk); };
    card.style.position="relative"; card.appendChild(pvb);
    card.addEventListener("dragstart",e=>{ mgDragSi=si; card.style.opacity=".45"; try{e.dataTransfer.setData("text/plain",String(si));}catch(_){} });
    card.addEventListener("dragend",()=>{ mgDragSi=-1; card.style.opacity=""; });
    card.addEventListener("dragover",e=>{ e.preventDefault(); });
    card.addEventListener("drop",e=>{ e.preventDefault(); if(mgDragSi<0||mgDragSi===si)return; const mv=mgSeq.splice(mgDragSi,1)[0]; mgSeq.splice(si,0,mv); mgDragSi=-1; renderMgBoard(); });
    grid.append(card); });
  const wrap=document.createElement("div"); wrap.className="boardScroll"; wrap.append(grid); box.append(hint,wrap);
  if(mgCurThumbDoc!==curDocId){ mgCurThumb=null; mgCurThumbDoc=curDocId; }
  if(mgSeq.some(t=>t.k==="cur") && !mgCurThumb && !mgCurThumbBusy && curDocId){ mgCurThumbBusy=true;
    call("/api/render",{doc_id:curDocId,page:0,zoom:0.16,password:docPw}).then(j=>{ mgCurThumb=j.png; mgCurThumbBusy=false; if(mgBoardUsed)renderMgBoard(); }).catch(()=>{ mgCurThumbBusy=false; }); } }
$("mgBoardBtn").onclick=()=>{ const b=$("mgBoard"); const show=b.style.display==="none";
  if(show){ mgBoardUsed=true; mgBuildSeq(); renderMgBoard(); b.style.display="flex"; b.style.flexDirection="column"; $("mgList").style.display="none"; $("mgPosWrap").style.display="none"; $("mgBoardBtn").textContent="🧩 Ocultar bloques"; $("mgDlg").querySelector(".box").classList.add("wide"); }
  else { b.style.display="none"; $("mgList").style.display="block"; $("mgPosWrap").style.display=(cur||curDocId)?"block":"none"; $("mgBoardBtn").textContent="🧩 Ordenar en bloques"; $("mgDlg").querySelector(".box").classList.remove("wide"); } };
async function doMergeAdopt(){ if(!mgItems.length)throw new Error("Añade al menos un PDF");
  let ids, nota="";
  if(mgBoardUsed && mgSeq){ ids=mgSeq.map(tk=>tk.k==="cur"?curDocId:tk.it.doc_id); nota="en el orden de los bloques"; }
  else { const files=mgItems.map(x=>x.doc_id);
    if((cur||curDocId)&&!mgExcludeCur){ const pos=document.querySelector('input[name="mgPos"]:checked').value;
      ids=pos==="end"?[curDocId,...files]:[...files,curDocId]; nota=pos==="end"?"al final":"al principio"; }
    else ids=files; }
  ids=ids.filter(Boolean);
  if(!ids.length)throw new Error("No hay ningún PDF para unir");
  $("mgDlg").style.display="none";
  const j=await callLong("/api/merge",{doc_ids:ids,light:1},"Unir los PDF");
  if(!j||(!j.doc_id&&!j.pdf))throw new Error("La unión no devolvió un documento: inténtalo de nuevo.");
  await adopt(j, (cur&&!mgExcludeCur)?curName:"unido.pdf");
  status("PDFs unidos ✔"+((cur&&!mgExcludeCur)?" ("+nota+" del documento que tenías)":"")+" — "+j.pages+" páginas en total"); }
$("mgOk").onclick=()=>run(doMergeAdopt);
$("bWord").onclick=()=>run(async()=>{ await need(); const j=await callLong("/api/to_word",{pdf:cur},"Convertir a Word");
  saveB64(j.file,"convertido.docx","application/vnd.openxmlformats-officedocument.wordprocessingml.document"); status("Word creado ✔ (formato aproximado, revísalo)"); });
$("bExcel").onclick=()=>run(async()=>{ await need(); const j=await callLong("/api/to_excel",{pdf:cur},"Convertir a Excel");
  saveB64(j.file,"convertido.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"); status("Excel creado ✔ ("+j.tables+" tabla(s) detectada(s))"); });
$("bToPng").onclick=()=>run(async()=>{ await need(); const j=await callLong("/api/to_images",{pdf:cur},"Convertir a imágenes PNG");
  saveB64(j.zip,"paginas_png.zip","application/zip"); status("Imágenes PNG listas ✔"); });
$("bToTxt").onclick=()=>run(async()=>{ await need(); const j=await callLong("/api/to_text",{pdf:cur},"Extraer el texto");
  $("txtOut").value=j.text; status("Texto extraído ✔ ("+j.pages+" páginas)"); });
$("bOcrTxt").onclick=()=>run(async()=>{ await need(); status("OCR en curso… puede tardar por página");
  const j=await callLong("/api/ocr_text",{pdf:cur,pages:""},"OCR: leyendo el texto"); $("txtOut").value=j.text; status("OCR terminado ✔ ("+j.pages+" página(s))"); });
const NOTE_POS={centro:[50,52,"c"],supcentro:[50,9,"c"],supizq:[7,9,"l"],supder:[93,9,"r"],infcentro:[50,94,"c"],infizq:[7,94,"l"],infder:[93,94,"r"]};
$("bNote").onclick=()=>run(async()=>{ await need(); const t=$("noteText").value; if(!t)throw new Error("Escribe el texto");
  const scope=$("noteScope").value, pos=$("notePos").value;
  const [x,y,al]=NOTE_POS[pos]; const pg=page;
  const j=await call("/api/add_text",{pdf:cur,page:pg,text:t,x_pct:x,y_pct:y,align:al,all:scope==="all"});
  await adopt(j,curName,true);
  status("Texto estampado ✔ ("+(scope==="all"?"en todas las páginas":"en esta página")+")"); });
$("bWm").onclick=()=>run(async()=>{ await need(); const j=await callLong("/api/watermark",{pdf:cur,text:$("wmText").value||"Aven PDF"},"Poner la marca de agua");
  await adopt(j,"con_marca.pdf",true); status("Marca de agua aplicada ✔"); });
$("wmImg").addEventListener("change",async e=>{ const f=e.target.files[0]; e.target.value=""; if(!f)return;
  run(async()=>{ await need(); const b64=await readB64(f);
    const j=await callLong("/api/watermark_image",{pdf:cur,image:b64,opacity:0.25},"Poner la marca de agua");
    await adopt(j,"con_marca.pdf",true); status("Imagen aplicada como marca de agua en todas las páginas ✔"); }); });
$("bRepl").onclick=()=>run(async()=>{ await need(); const o=$("findTxt").value; if(!o)throw new Error("Escribe el texto a buscar");
  const j=await callLong("/api/replace_text",{pdf:cur,old:o,new:$("replTxt").value,pages:""},"Buscar y reemplazar");
  if(!j.replaced){ status("No encontré ese texto en el PDF.",false); return; }
  await adopt(j,"editado.pdf",true); status("Texto reemplazado en "+j.replaced+" lugar(es) ✔"); });
$("bEnc").onclick=()=>run(async()=>{ await need(); const p=$("newPw").value; if(!p)throw new Error("Escribe la contraseña nueva");
  const j=await call("/api/encrypt",{pdf:cur,password:p}); docPw=p; $("newPw").value=""; await adopt(j,"protegido.pdf",true); $("pwDlg").style.display="flex"; status("PDF protegido con AES-256 ✔"); });
$("bDec").onclick=()=>run(async()=>{ await need(); $("decPwIn").value=docPw; $("decDlg").style.display="flex"; setTimeout(()=>$("decPwIn").focus(),60); });
$("decCancel").onclick=()=>{ $("decDlg").style.display="none"; };
$("decOk").onclick=()=>run(async()=>{ const p=$("decPwIn").value; if(!p)throw new Error("Escribe la contraseña actual del PDF");
  $("decDlg").style.display="none";
  const j=await call("/api/decrypt",{pdf:cur,password:p}); docPw=""; await adopt(j,"sin_clave.pdf",true); status("Contraseña retirada ✔"); });
$("decPwIn").addEventListener("keydown",e=>{ if(e.key==="Enter")$("decOk").click(); });
$("bComp").onclick=()=>run(async()=>{ await need();
  const kb=curSizeKB||Math.round((cur?cur.length*0.75:0)/1024);
  $("cpInfo").textContent="Tamaño actual: "+fmtSize(kb)+". Comprimir achica las imágenes que trae el PDF (en un escaneo, casi todo el peso está ahí).";
  updCpEst(); $("cpDlg").style.display="flex"; });
function fmtSize(kb){ if(kb==null||isNaN(kb))return "—"; if(kb>=1048576)return (kb/1048576).toLocaleString("es",{maximumFractionDigits:2})+" GB"; if(kb>=1024)return (kb/1024).toLocaleString("es",{maximumFractionDigits:2})+" MB"; return Math.round(kb).toLocaleString("es")+" KB"; }
function updCpEst(){ const kb=curSizeKB||Math.round((cur?cur.length*0.75:0)/1024); if(!kb){ $("cpEst").textContent=""; return; }
  const lv=document.querySelector('input[name="cpLv"]:checked').value;
  const r={pantalla:[15,45],media:[40,70],alta:[70,90]}[lv];
  $("cpEst").textContent="Resultado estimado: de "+fmtSize(kb)+" a unos "+fmtSize(Math.round(kb*r[0]/100))+"–"+fmtSize(Math.round(kb*r[1]/100))+". Estimación para escaneos y fotos; si el PDF es texto digital, casi no bajará (el peso exacto sale al terminar)."; }
document.querySelectorAll('input[name="cpLv"]').forEach(r=>r.addEventListener("change",updCpEst));
$("cpCancel").onclick=()=>$("cpDlg").style.display="none";
$("cpOk").onclick=()=>run(async()=>{ const lv=document.querySelector('input[name="cpLv"]:checked').value; $("cpDlg").style.display="none";
  const j=await callLong("/api/compress",{pdf:cur,password:docPw,level:lv},"Comprimir el PDF"); await adopt(j,"optimizado.pdf",true);
  if(j.after_kb<j.before_kb){ const pct=Math.round(100*(1-j.after_kb/j.before_kb));
    status(`Comprimido de verdad: ${fmtSize(j.before_kb)} → ${fmtSize(j.after_kb)} (−${pct}%, ${j.images_done} imágenes reducidas) ✔ — Descargar o Guardar para conservarlo`); }
  else { askInfo("Con este nivel el tamaño no bajó ("+fmtSize(j.before_kb)+" → "+fmtSize(j.after_kb)+"; imágenes reducidas: "+j.images_done+"). Si el documento es de escaneos, prueba el nivel «Pantalla», que es el que más achica."); }
});
$("bTxtClear").onclick=()=>{ $("txtOut").value=""; status("Texto limpiado ✔"); };
$("bTxtBig").onclick=()=>{ if(!$("txtOut").value){ showErr("Todavía no hay texto: primero extrae el texto del PDF o usa el OCR."); return; }
  $("txtBig").value=$("txtOut").value; $("txtDlg").style.display="flex"; };
$("txtClose").onclick=()=>{ $("txtDlg").style.display="none"; };
$("txtCopy").onclick=async()=>{ try{ await navigator.clipboard.writeText($("txtBig").value); status("Texto copiado ✔"); }catch(e){ $("txtBig").select(); document.execCommand("copy"); status("Texto copiado ✔"); } };
function specFromDlg(pre){ const mode=document.querySelector('input[name="'+pre+'Mode"]:checked').value;
  if(mode==="all"||mode==="auto") return "";
  if(mode==="range"){ const a=parseInt($(pre+"From").value||"1",10), b=parseInt($(pre+"To").value||"1",10);
    if(!(a>=1&&b>=a&&b<=pages))throw new Error("Rango no válido: debe ir del 1 al "+pages+" y «desde» no puede ser mayor que «hasta»");
    return a+"-"+b; }
  const v=$(pre+"List").value.trim(); if(!v)throw new Error("Escribe las páginas, p. ej. 2, 5, 7"); return v; }
$("bExtImg").onclick=()=>run(async()=>{ await need(); $("xiTo").value=pages; $("xiTotal").textContent="(el documento tiene "+pages+")"; $("xiDlg").style.display="flex"; });
$("xiCancel").onclick=()=>{ $("xiDlg").style.display="none"; };
$("xiOk").onclick=()=>run(async()=>{ const spec=specFromDlg("xi"); $("xiDlg").style.display="none";
  const j=await callLong("/api/extract_images",{pdf:cur,pages:spec,password:docPw},"Extraer imágenes");
  if(!j.count){ askInfo("Se encontraron 0 imágenes incrustadas en las páginas elegidas.\n\nOjo: «Extraer imágenes» saca las fotos que el PDF trae dentro; si lo que quieres es cada página como foto, usa «a imágenes PNG»."); status("Sin imágenes incrustadas en esas páginas."); return; }
  dlNote="Se encontraron "+j.count+" imagen(es) dentro del documento (en "+j.pages+" página(s) revisada(s)).";
  saveB64(j.zip,"imagenes_extraidas.zip","application/zip");
  status("Imágenes extraídas ✔ "+j.count+" encontrada(s)"); });
$("bScan").onclick=()=>run(async()=>{ await need(); $("scDlg").style.display="flex"; });
$("scCancel").onclick=()=>{ $("scDlg").style.display="none"; };
$("scOk").onclick=()=>run(async()=>{ const mode=document.querySelector('input[name="scMode"]:checked').value;
  $("scDlg").style.display="none"; status("Convirtiendo a PDF escaneado… puede tardar por página");
  const j=await callLong("/api/to_scanned",{pdf:cur,mode,password:docPw},"Crear el PDF escaneado");
  await adopt(j,"escaneado.pdf",true); status("PDF escaneado creado ✔ ("+j.pages+" páginas, modo "+(mode==="bw"?"blanco y negro":"color")+")"); });
$("bDeskew").onclick=()=>run(async()=>{ await need(); $("dkTo").value=pages; $("dkTotal").textContent="(el documento tiene "+pages+")"; $("dkDlg").style.display="flex"; });
$("dkCancel").onclick=()=>{ $("dkDlg").style.display="none"; };
$("dkOk").onclick=()=>run(async()=>{ const spec=specFromDlg("dk"); $("dkDlg").style.display="none"; status("Enderezando… puede tardar por página");
  const j=await callLong("/api/deskew",{pdf:cur,pages:spec,password:docPw},"Enderezar páginas");
  await adopt(j,"enderezado.pdf",true);
  status(j.fixed?("Enderezado ✔ "+j.fixed+" página(s) corregida(s)"):"Sin cambios: ninguna página estaba chueca ✔"); });
$("bFields").onclick=()=>run(async()=>{ await need(); const j=await call("/api/form_fields",{pdf:cur});
  const box=$("fieldsBox"); box.innerHTML="";
  if(!j.fields.length){ box.textContent="Este PDF no tiene campos de formulario."; return; }
  j.fields.forEach(f=>{ const lab=document.createElement("label"); lab.textContent=f.name;
    const inp=document.createElement("input"); inp.type="text"; inp.value=f.value||""; inp.dataset.name=f.name; inp.className="ff";
    box.appendChild(lab); box.appendChild(inp); box.appendChild(document.createElement("br")); });
  const b=document.createElement("button"); b.className="bigbtn"; b.textContent="Guardar formulario rellenado";
  b.onclick=()=>run(async()=>{ const vals={}; document.querySelectorAll(".ff").forEach(i=>vals[i.dataset.name]=i.value);
    const j2=await call("/api/fill_form",{pdf:cur,values:vals}); await adopt(j2,"formulario.pdf",true); status("Formulario guardado ✔"); });
  box.appendChild(b); status(j.fields.length+" campo(s) encontrado(s) ✔"); });
  call("/api/winmode",{}).then(j=>{ const e=document.getElementById("winMode"); if(e&&j&&j.mode) e.textContent="· ventana: "+j.mode; }).catch(()=>{});

// ---------- certificados en bloque v2 (1.21): datos ubicados con clics ----------
let certTplB64=null, certXlB64=null, certInfoOk=false, certDocId=null, certPages=0, certPage=0;
let certFields=[], certMarkers=[], certDims=[0,0];
function certAllNames(){ const ns=certFields.map(f=>f.name).filter(Boolean); return [...new Set([...ns,...certMarkers])]; }
function certReset(){ certTplB64=null; certXlB64=null; certInfoOk=false; certDocId=null; certPages=0; certPage=0; certFields=[]; certMarkers=[]; certDims=[0,0];
  $("certTplName").textContent="Ningún archivo"; $("certXlName").textContent="Ningún archivo"; $("certScanInfo").textContent="";
  $("certMapWrap").style.display="none"; $("certFields").innerHTML=""; $("certNameCol").innerHTML=""; $("certTplXl").disabled=true;
  $("certInfo").textContent="Elige el modelo: si tu certificado ya trae datos como {{nombre}} se detectan solos; si no, ubícalos con clics."; $("certGo").disabled=true; }
$("bCert").onclick=()=>{ certReset(); $("certDlg").style.display="flex"; };
$("certCancel").onclick=()=>{ $("certDlg").style.display="none"; };
$("certTplBtn").onclick=()=>$("certTplFile").click();
$("certXlBtn").onclick=()=>$("certXlFile").click();
$("certTplFile").onchange=async e=>{ const f=e.target.files[0]; e.target.value=""; if(!f)return;
  certTplB64=await readB64(f); $("certTplName").textContent=f.name;
  try{ const o=await call("/api/open",{pdf:certTplB64}); certDocId=o.doc_id; certPages=o.pages;
    const sc=await call("/api/cert_scan",{doc_id:certDocId}); certMarkers=sc.markers||[];
    $("certScanInfo").textContent=certMarkers.length?("Marcadores detectados: "+certMarkers.map(m=>"{{"+m+"}}").join(", ")+" (se ubican solos)"):"Sin marcadores: ubica los datos con clics en el modelo";
    certPage=0; $("certMapWrap").style.display="block"; renderCertFields(); await certShowPage(); certSyncNames(); certCheck();
  }catch(err){ errMsg(err.message); } };
async function certShowPage(){ if(!certDocId)return;
  const j=await call("/api/render",{doc_id:certDocId,page:certPage,zoom:1});
  certDims=[j.w,j.h]; $("certMap").src="data:image/png;base64,"+j.png;
  $("certPgLbl").textContent="Página "+(certPage+1)+" de "+certPages; certPins(); }
$("certPrev").onclick=()=>{ if(certPage>0){ certPage--; certShowPage(); } };
$("certNext").onclick=()=>{ if(certPage<certPages-1){ certPage++; certShowPage(); } };
$("certMap").onclick=e=>{ if(!certDims[0])return; const r=e.target.getBoundingClientRect();
  const x=(e.clientX-r.left)/r.width*certDims[0], y=(e.clientY-r.top)/r.height*certDims[1];
  certFields.push({name:"Dato "+(certFields.length+1),page:certPage,x:Math.round(x),y:Math.round(y),size:16,bold:false,align:"centro",color:"#000000"});
  renderCertFields(); certPins(); certSyncNames(); certCheck(); };
function certPins(){ document.querySelectorAll(".certpin").forEach(p=>p.remove()); if(!certDims[0])return;
  const st=$("certStageInner");
  certFields.forEach((f,i)=>{ if(f.page!==certPage)return; const p=document.createElement("div"); p.className="certpin";
    p.textContent=i+1; p.style.left=(f.x/certDims[0]*100)+"%"; p.style.top=(f.y/certDims[1]*100)+"%"; st.appendChild(p); }); }
function renderCertFields(){ const box=$("certFields"); box.innerHTML="";
  if(!certFields.length){ box.innerHTML="<div style='font-size:12.5px;color:#64748B'>Aún no ubicas datos: haz clic en el certificado, donde va el nombre, el curso, la fecha…</div>"; return; }
  certFields.forEach((f,i)=>{ const row=document.createElement("div"); row.style.cssText="display:flex;gap:6px;align-items:center;margin:4px 0;flex-wrap:wrap";
    const badge=document.createElement("span"); badge.className="certbadge"; badge.textContent=i+1;
    const nm=document.createElement("input"); nm.type="text"; nm.value=f.name; nm.style.width="130px"; nm.title="Nombre del dato (así se llamará la columna en el Excel)";
    nm.onchange=()=>{ f.name=nm.value.trim()||f.name; nm.value=f.name; certSyncNames(); certCheck(); };
    const sz=document.createElement("input"); sz.type="number"; sz.value=f.size; sz.min=6; sz.max=72; sz.style.width="58px"; sz.title="Tamaño de letra";
    sz.onchange=()=>{ f.size=Math.max(6,Math.min(72,parseFloat(sz.value)||16)); };
    const bd=document.createElement("label"); bd.style.fontSize="12.5px"; const bc=document.createElement("input"); bc.type="checkbox"; bc.checked=!!f.bold; bc.onchange=()=>{ f.bold=bc.checked; }; bd.append(bc," Negrita");
    const al=document.createElement("select"); al.innerHTML="<option value='centro'>Centrado</option><option value='izquierda'>Izquierda</option><option value='derecha'>Derecha</option>"; al.value=f.align; al.title="Alineación desde el punto del clic"; al.onchange=()=>{ f.align=al.value; };
    const cl=document.createElement("input"); cl.type="color"; cl.value=f.color; cl.onchange=()=>{ f.color=cl.value; };
    const pg=document.createElement("span"); pg.style.cssText="font-size:12px;color:#64748B"; pg.textContent="pág. "+(f.page+1);
    const del=document.createElement("button"); del.textContent="✖"; del.title="Quitar este dato"; del.onclick=()=>{ certFields.splice(i,1); renderCertFields(); certPins(); certSyncNames(); certCheck(); };
    row.append(badge,nm,sz,bd,al,cl,pg,del); box.appendChild(row); }); }
function certSyncNames(){ $("certTplXl").disabled=!certAllNames().length;
  if(certXlB64)return;
  const nc=$("certNameCol"); const prev=nc.value;
  nc.innerHTML=certAllNames().map(n=>'<option value="'+String(n).replace(/"/g,"&quot;")+'">'+n+"</option>").join("");
  if(prev&&certAllNames().includes(prev))nc.value=prev; }
$("certTplXl").onclick=async()=>{ try{ const j=await call("/api/cert_template",{names:certAllNames()});
    const r=await fetch(j.dlf); if(!r.ok)throw new Error("No se pudo descargar la plantilla");
    const blob=await r.blob(); const u=URL.createObjectURL(blob); const t=document.createElement("a"); t.href=u; t.download="plantilla_certificados.xlsx"; document.body.appendChild(t); t.click(); t.remove(); setTimeout(()=>URL.revokeObjectURL(u),4000);
    status("Plantilla descargada ✔ Llénala (una fila = un certificado) y súbela como base Excel."); }catch(e){ errMsg(e.message); } };
$("certXlFile").onchange=async e=>{ const f=e.target.files[0]; e.target.value=""; if(!f)return; certXlB64=await readB64(f); $("certXlName").textContent=f.name; certCheck(); };
async function certCheck(){ certInfoOk=false; $("certGo").disabled=true;
  if(!certTplB64||!certXlB64){ if(certTplB64&&!certXlB64)$("certInfo").textContent="Modelo listo. Descarga la plantilla, llénala y súbela como base Excel (o sube tu Excel si las columnas se llaman como los datos)."; return; }
  $("certInfo").textContent="Revisando la base contra los datos ubicados…";
  try{ const j=await call("/api/cert_info",{template:certTplB64,excel:certXlB64,names:certFields.map(f=>f.name)});
    certInfoOk=true;
    const miss=(j.missing&&j.missing.length)? '<br><span style="color:#B91C1C"><b>Sin columna en el Excel</b> (quedarán en blanco): '+j.missing.join(", ")+"</span>":"";
    $("certInfo").innerHTML="<b>"+j.rows+" certificados</b> por generar (una fila = uno)."+miss;
    const nc=$("certNameCol"); const cols=j.columns||[]; const prev=nc.value;
    nc.innerHTML=cols.map(c=>'<option value="'+String(c).replace(/"/g,"&quot;")+'">'+c+"</option>").join("");
    if(prev&&cols.includes(prev))nc.value=prev;
    $("certGo").disabled=false;
  }catch(e){ $("certInfo").innerHTML='<span style="color:#B91C1C">'+e.message+"</span>"; } }
$("certLimitSel").onchange=()=>{ $("certLimitN").style.display=$("certLimitSel").value==="n"?"inline-block":"none"; };
$("certGo").onclick=async()=>{ if(!certInfoOk)return;
  const lim=$("certLimitSel").value==="n"?(parseInt($("certLimitN").value)||0):0;
  $("certDlg").style.display="none";
  try{ const j=await callLong("/api/cert_bulk",{template:certTplB64,excel:certXlB64,name_col:$("certNameCol").value||null,fields:certFields,limit:lim},"Generar certificados");
    const r=await fetch(j.dlf); if(!r.ok) throw new Error("No se pudo descargar el ZIP de certificados");
    const blob=await r.blob(); const u=URL.createObjectURL(blob);
    const t=document.createElement("a"); t.href=u; t.download="certificados.zip"; document.body.appendChild(t); t.click(); t.remove();
    setTimeout(()=>URL.revokeObjectURL(u),4000);
    msg("Certificados listos","Se generaron <b>"+j.count+" certificados</b> en el archivo <b>certificados.zip</b> ("+j.zip_mb+" MB), uno por cada fila de tu base.");
  }catch(e){ if(!/Cancelado/.test(e.message)) errMsg(e.message); } };


// ---------- abrir varios PDF (1.21) ----------
let pendingMulti=null;
async function mgAddFiles(list){ const fs=[...list].filter(f=>/\.pdf$/i.test(f.name)||f.type==="application/pdf");
  for(let n=0;n<fs.length;n++){ const f=fs[n];
    status("Cargando "+(n+1)+" de "+fs.length+" …");
    const b64=await readB64(f);
    const inf=await call("/api/open",{pdf:b64,thumb:1});
    if(!inf.doc_id) throw new Error("No se pudo cargar «"+f.name+"»");
    mgItems.push({name:f.name,doc_id:inf.doc_id,pages:inf.pages,thumb:inf.thumb||null});
    if(mgBoardUsed&&mgSeq)mgSeq.push({k:"f",it:mgItems[mgItems.length-1]}); }
  renderMg(); if(mgBoardUsed)renderMgBoard(); }
function mgShowBoard(){ mgBoardUsed=true; mgBuildSeq(); renderMgBoard(); $("mgBoard").style.display="flex"; $("mgBoard").style.flexDirection="column"; $("mgList").style.display="none"; $("mgPosWrap").style.display="none"; $("mgBoardBtn").textContent="🧩 Ocultar bloques"; $("mgDlg").querySelector(".box").classList.add("wide"); }
let pendingMultiReplace=false;
function openMultiDlg(files,asReplace){ pendingMulti=[...files]; pendingMultiReplace=!!asReplace;
  $("multiTxt").textContent="Elegiste "+files.length+" PDF. "+(pendingMultiReplace?("Reemplazarán al documento que tienes abierto ("+curName+"): se cargarán como un documento nuevo."):((cur||curDocId)?("Se añadirán al documento que tienes abierto ("+curName+")."):("Se cargarán como un solo documento.")));
  $("multiDlg").style.display="flex"; }
$("multiCancel").onclick=()=>{ $("multiDlg").style.display="none"; pendingMulti=null; pendingMultiReplace=false; };
$("multiLoad").onclick=()=>{ const fs=pendingMulti; pendingMulti=null; $("multiDlg").style.display="none";
  if(!fs)return; mgExcludeCur=pendingMultiReplace; pendingMultiReplace=false;
  run(async()=>{ mgItems=[]; mgSeq=null; mgBoardUsed=false; await mgAddFiles(fs); try{ await doMergeAdopt(); }finally{ mgExcludeCur=false; } }); };
$("multiOrder").onclick=()=>{ const fs=pendingMulti; pendingMulti=null; $("multiDlg").style.display="none";
  if(!fs)return; mgExcludeCur=pendingMultiReplace; pendingMultiReplace=false;
  run(async()=>{ mgItems=[]; mgSeq=null; renderMg(); mgShowBoard(); await mgAddFiles(fs); $("mgDlg").style.display="flex"; }); };
$("emptyPlus").onclick=()=>$("bOpenLbl").click();

// ---------- abrir con documento abierto: el usuario elige (1.24) ----------
let pendingOpenFiles=null;
async function singleOpen(f){ fileHandle=null; wipeViewer("Cargando "+f.name+"…");
  const b64=await readB64(f); run(async()=>{ await tryOpen(b64, f.name, "PDF cargado ✔ (el anterior se cerró)"); }); }
function handleChosenFiles(fs){ fs=[...fs].filter(f=>/\.pdf$/i.test(f.name)||f.type==="application/pdf"); if(!fs.length)return;
  if(!(cur||curDocId)){ if(fs.length>1)openMultiDlg(fs); else singleOpen(fs[0]); return; }
  pendingOpenFiles=fs;
  $("ocTxt").textContent="Tienes abierto «"+curName+"». Con "+(fs.length>1?("los "+fs.length+" PDF elegidos"):("«"+fs[0].name+"»"))+" puedes:";
  $("openChoiceDlg").style.display="flex"; }
$("ocCancel").onclick=()=>{ $("openChoiceDlg").style.display="none"; pendingOpenFiles=null; };
$("ocAdd").onclick=()=>{ const fs=pendingOpenFiles; pendingOpenFiles=null; $("openChoiceDlg").style.display="none"; if(!fs)return;
  run(async()=>{ mgExcludeCur=false; mgItems=[]; mgSeq=null; mgBoardUsed=false; await mgAddFiles(fs); await doMergeAdopt(); }); };
$("ocReplace").onclick=()=>{ const fs=pendingOpenFiles; pendingOpenFiles=null; $("openChoiceDlg").style.display="none"; if(!fs)return;
  if(fs.length===1){ singleOpen(fs[0]); return; }
  run(async()=>{ mgExcludeCur=true; mgItems=[]; mgSeq=null; mgBoardUsed=false; await mgAddFiles(fs); await doMergeAdopt(); }); };
// ---------- Editor de la cinta (1.26): Con ajuste / Libre, sin tocar la lógica ----------
const RBKEY="avenRibbonV3", RBOLD="avenRibbonV1";
let rbEditing=false, rbDragEl=null, rbEntry=null, rbOriginal=null, rbMode="ajuste", rbDragged=false;
const RBSEL="#tabs button, .ribbon button, .ribbon .bigbtn";
function rbKey(el){ return el.id?("i:"+el.id):(el.dataset.rbid?("d:"+el.dataset.rbid):("g:"+(el.dataset.grp||""))); }
function rbEl(key){ if(!key)return null; if(key.startsWith("i:"))return document.getElementById(key.slice(2)); if(key.startsWith("g:"))return document.querySelector('[data-grp="'+key.slice(2)+']'); return document.querySelector('[data-rbid="'+key.slice(2)+']'); }
function rbAssign(){ let n=0;
  document.querySelectorAll(".ribbon button, .ribbon .bigbtn").forEach(el=>{ if(!el.id&&!el.dataset.rbid) el.dataset.rbid="rb"+(n++); });
  document.querySelectorAll(".ribbon").forEach(p=>{ let gi=0;
    p.querySelectorAll(":scope > .grp").forEach(g=>{ g.dataset.grp=p.id+":"+gi; gi++; let ri=0;
      g.querySelectorAll(".rowbtns").forEach(r=>{ r.dataset.rbc=g.dataset.grp+"r"+ri; ri++; }); }); }); }
function rbContKey(el){ const r=el.closest(".rowbtns"); if(r&&r.dataset.rbc) return "c:"+r.dataset.rbc;
  const g=el.closest(".grp"); return g?("c:"+g.dataset.grp):null; }
function rbContEl(key){ if(!key)return null; const k=key.slice(2);
  return document.querySelector('[data-rbc="'+k+'"]')||document.querySelector('[data-grp="'+k+'"]'); }
function rbSerialize(){ const tabs=[...document.querySelectorAll("#tabs button")].map(b=>b.dataset.t);
  const conts={};
  document.querySelectorAll(".ribbon button, .ribbon .bigbtn").forEach(el=>{ const ck=rbContKey(el); if(ck){ (conts[ck]=conts[ck]||[]).push(rbKey(el)); } });
  const groups={};
  document.querySelectorAll(".ribbon").forEach(p=>{ groups[p.id]=[...p.querySelectorAll(":scope > .grp")].map(g=>g.dataset.grp); });
  return {tabs:tabs, conts:conts, groups:groups}; }
function rbHideEmpty(){ if(rbMode==="libre")return;
  document.querySelectorAll(".ribbon .grp, .ribbon .rowbtns").forEach(c=>{
    const has=c.querySelector("button, .bigbtn, input, select, textarea");
    c.style.display=(!rbEditing&&!has)?"none":""; }); }
function rbApply(L){ if(!L)return;
  if(L.tabs){ const bar=$("tabs"); L.tabs.forEach(t=>{ const b=bar.querySelector('button[data-t="'+t+'"]'); if(b)bar.appendChild(b); }); }
  if(L.groups){ Object.keys(L.groups).forEach(pid=>{ const p=document.getElementById(pid); if(!p)return;
    L.groups[pid].forEach(gk=>{ const g=p.querySelector('[data-grp="'+gk+'"]'); if(g)p.appendChild(g); }); }); }
  if(L.conts){ Object.keys(L.conts).forEach(ck=>{ const c=rbContEl(ck); if(!c)return;
    L.conts[ck].forEach(k=>{ const el=rbEl(k); if(el)c.appendChild(el); }); }); }
  rbHideEmpty(); }
function rbContainers(){ return [$("tabs"), ...document.querySelectorAll(".ribbon")]; }
function rbMovablesIn(cont){ if(cont.id==="tabs") return [...cont.querySelectorAll("button")];
  const gs=[...cont.children].filter(el=>el.classList&&el.classList.contains("grp"));
  return gs.length?gs:[...cont.children]; }
function rbWithLayout(cont, fn){ const wasOn=cont.classList.contains("on")||cont.id==="tabs";
  if(!wasOn){ cont.classList.add("on"); cont.style.visibility="hidden"; }
  try{ fn(); } finally { if(!wasOn){ cont.classList.remove("on"); cont.style.visibility=""; } } }
function rbFreeConvert(){ rbContainers().forEach(cont=>{ if(cont.dataset.free)return;
  rbWithLayout(cont, ()=>{ const movs=rbMovablesIn(cont);
    const snap=movs.map(el=>[el, el.offsetLeft, el.offsetTop, el.offsetWidth, el.offsetHeight]);
    cont.style.position="relative";
    let maxB=0;
    snap.forEach(pr=>{ const el=pr[0];
      el.style.position="absolute"; el.style.left=pr[1]+"px"; el.style.top=pr[2]+"px"; el.style.width=pr[3]+"px"; el.style.height=pr[4]+"px"; el.style.margin="0"; el.style.zIndex="3";
      maxB=Math.max(maxB, pr[2]+pr[4]); });
    cont.style.minHeight=(maxB+10)+"px"; cont.dataset.free="1"; }); }); }
function rbFreeUnconvert(){ rbContainers().forEach(cont=>{ if(!cont.dataset.free)return;
  rbMovablesIn(cont).forEach(el=>{ ["position","left","top","width","height","margin","zIndex"].forEach(p=>el.style[p]=""); });
  cont.style.minHeight=""; delete cont.dataset.free; });
  document.querySelectorAll(".rbHandle").forEach(h=>h.remove()); }
function rbFreeSerialize(){ const out={};
  rbContainers().forEach(cont=>{ if(!cont.dataset.free)return; const m={};
    rbMovablesIn(cont).forEach(el=>{ m[rbKey(el)]={x:el.offsetLeft, y:el.offsetTop, w:el.offsetWidth, h:el.offsetHeight}; });
    out[cont.id]=m; });
  return out; }
function rbFreeApply(data){ if(!data)return;
  rbContainers().forEach(cont=>{ const m=data[cont.id]; if(!m)return;
    rbWithLayout(cont, ()=>{ cont.style.position="relative"; let maxB=0;
      Object.keys(m).forEach(k=>{ const el=rbEl(k); if(!el)return; const r=m[k];
        el.style.position="absolute"; el.style.left=r.x+"px"; el.style.top=r.y+"px"; el.style.width=r.w+"px"; el.style.height=r.h+"px"; el.style.margin="0"; el.style.zIndex="3";
        maxB=Math.max(maxB, r.y+r.h); });
      cont.style.minHeight=(maxB+10)+"px"; cont.dataset.free="1"; }); }); }
function rbAddHandles(){ if(!rbEditing||rbMode!=="libre")return;
  rbContainers().forEach(cont=>{ rbMovablesIn(cont).forEach(el=>{ if(el.querySelector(":scope > .rbHandle"))return; const s=document.createElement("span"); s.className="rbHandle"; el.appendChild(s); }); }); }
function rbCapture(){ return {mode:rbMode, snap:rbSerialize(), free:rbFreeSerialize()}; }
function rbModeBtns(){ const a=$("rbModeSnap"), b=$("rbModeFree"); if(a)a.classList.toggle("on", rbMode==="ajuste"); if(b)b.classList.toggle("on", rbMode==="libre"); }
function rbRestore(st){ if(!st)return;
  rbFreeUnconvert();
  if(st.snap) rbApply(st.snap);
  rbMode=st.mode||"ajuste";
  if(rbMode==="libre"){ if(st.free&&Object.keys(st.free).length) rbFreeApply(st.free); else rbFreeConvert(); rbAddHandles(); }
  rbModeBtns(); rbHideEmpty(); }
function rbSetMode(m){ if(m===rbMode)return;
  if(m==="libre"){ rbMode="libre"; rbFreeConvert(); rbAddHandles(); }
  else { rbMode="ajuste"; rbFreeUnconvert(); rbHideEmpty(); }
  rbModeBtns(); rbSetDrag(rbEditing&&rbMode==="ajuste"); }
function rbSetDrag(on){ document.querySelectorAll(RBSEL).forEach(el=>{ el.draggable=on; }); }
function rbEnter(){ if(rbEditing)return; rbEntry=rbCapture(); rbEditing=true;
  document.body.classList.add("rbedit"); $("rbBar").style.display="flex";
  rbSetDrag(rbMode==="ajuste"); if(rbMode==="libre")rbAddHandles(); rbHideEmpty();
  status("Modo editor activo: «Con ajuste» acomoda los botones en los espacios; «Libre» los pone donde quieras y del tamaño que quieras."); }
function rbExit(){ rbEditing=false; document.body.classList.remove("rbedit"); $("rbBar").style.display="none"; rbSetDrag(false);
  document.querySelectorAll(".rbHandle").forEach(h=>h.remove()); rbHideEmpty(); }
$("bRibbonEdit").onclick=()=>rbEnter();
$("rbModeSnap").onclick=()=>rbSetMode("ajuste");
$("rbModeFree").onclick=()=>rbSetMode("libre");
$("rbSave").onclick=()=>{ const st=rbCapture(); try{ localStorage.setItem(RBKEY, JSON.stringify(st)); localStorage.removeItem(RBOLD); }catch(_){ }
  rbExit(); status("Orden de la cinta guardado ✔ Así quedará cada vez que abras Aven PDF."); };
$("rbExit").onclick=()=>{ if(rbEntry) rbRestore(rbEntry); rbExit(); status("Cambios del orden descartados: la cinta quedó como estaba."); };
$("rbReset").onclick=()=>{ try{ localStorage.removeItem(RBKEY); localStorage.removeItem(RBOLD); }catch(_){ }
  rbRestore({mode:"ajuste", snap:rbOriginal, free:{}}); rbEntry=rbCapture();
  status("Orden original restablecido ✔ Si te gusta así, dale Guardar."); };
document.addEventListener("click",e=>{ if(!rbEditing)return;
  if(rbDragged && e.target.closest && e.target.closest("#tabs")){ rbDragged=false; e.preventDefault(); e.stopPropagation(); return; }
  if(e.target.closest && e.target.closest(".ribbon")){ e.preventDefault(); e.stopPropagation(); } },true);
document.addEventListener("dragstart",e=>{ if(!rbEditing||rbMode!=="ajuste")return;
  const m=e.target.closest(RBSEL); if(!m)return;
  rbDragEl=m; m.classList.add("rbdrag");
  try{ e.dataTransfer.setData("text/plain","rb"); e.dataTransfer.effectAllowed="move"; }catch(_){ } });
document.addEventListener("dragend",()=>{ if(rbDragEl)rbDragEl.classList.remove("rbdrag"); rbDragEl=null;
  document.querySelectorAll(".rbov").forEach(x=>x.classList.remove("rbov")); });
function rbTarget(e){ const m=e.target.closest(RBSEL); if(m)return {el:m};
  const c=e.target.closest(".ribbon .grp, .ribbon .rowbtns, #tabs"); return c?{cont:c}:null; }
document.addEventListener("dragover",e=>{ if(!rbEditing||rbMode!=="ajuste"||!rbDragEl)return; const t=rbTarget(e); if(!t)return;
  e.preventDefault(); try{ e.dataTransfer.dropEffect="move"; }catch(_){ }
  document.querySelectorAll(".rbov").forEach(x=>x.classList.remove("rbov"));
  if(t.el&&t.el!==rbDragEl) t.el.classList.add("rbov"); });
document.addEventListener("drop",e=>{ if(!rbEditing||rbMode!=="ajuste"||!rbDragEl)return; const t=rbTarget(e); if(!t)return;
  e.preventDefault();
  if(t.el&&t.el!==rbDragEl){ const r=t.el.getBoundingClientRect();
    const row=getComputedStyle(t.el.parentElement).flexDirection.indexOf("row")===0;
    const after=row?(e.clientX>r.left+r.width/2):(e.clientY>r.top+r.height/2);
    t.el.parentElement.insertBefore(rbDragEl, after?t.el.nextSibling:t.el); }
  else if(t.cont){ t.cont.appendChild(rbDragEl); }
  document.querySelectorAll(".rbov").forEach(x=>x.classList.remove("rbov")); });
let rbPtr=null;
document.addEventListener("pointerdown",e=>{ if(!rbEditing||rbMode!=="libre")return;
  const hd=e.target.closest?e.target.closest(".rbHandle"):null;
  const m=hd?hd.parentElement:(e.target.closest?e.target.closest("#tabs button, .ribbon .grp"):null);
  if(!m||m.style.position!=="absolute")return;
  rbPtr={el:m, resize:!!hd, x:e.clientX, y:e.clientY, L:m.offsetLeft, T:m.offsetTop, W:m.offsetWidth, H:m.offsetHeight, moved:false};
  if(!m.closest("#tabs")) e.preventDefault(); });
document.addEventListener("pointermove",e=>{ if(!rbPtr)return; const dx=e.clientX-rbPtr.x, dy=e.clientY-rbPtr.y;
  if(Math.abs(dx)+Math.abs(dy)>3) rbPtr.moved=true;
  if(rbPtr.resize){ rbPtr.el.style.width=Math.max(44, rbPtr.W+dx)+"px"; rbPtr.el.style.height=Math.max(30, rbPtr.H+dy)+"px"; }
  else { rbPtr.el.style.left=Math.max(0, rbPtr.L+dx)+"px"; rbPtr.el.style.top=Math.max(0, rbPtr.T+dy)+"px"; } });
document.addEventListener("pointerup",()=>{ if(rbPtr&&rbPtr.moved) rbDragged=true; rbPtr=null; });
const tipFloat=document.createElement("div"); tipFloat.id="tipFloat"; document.body.appendChild(tipFloat);
document.addEventListener("mouseover",e=>{ const t=e.target.closest?e.target.closest("[data-tip]"):null;
  if(!t){ tipFloat.style.display="none"; return; }
  tipFloat.textContent=t.getAttribute("data-tip"); const r=t.getBoundingClientRect();
  tipFloat.style.display="block";
  tipFloat.style.left=Math.max(6, Math.min(window.innerWidth-336, r.left+r.width/2-165))+"px";
  tipFloat.style.top=(r.bottom+8)+"px"; });
document.addEventListener("mouseout",e=>{ if(e.target.closest&&e.target.closest("[data-tip]")) tipFloat.style.display="none"; });
rbAssign(); rbOriginal=rbSerialize();
try{ let saved=null; const s2=localStorage.getItem(RBKEY);
  if(s2) saved=JSON.parse(s2);
  else { const sOld=localStorage.getItem("avenRibbonV2"); if(sOld){ const pOld=JSON.parse(sOld); saved={mode:pOld.mode||"ajuste", snap:pOld.snap, free:{}}; } else { const s1=localStorage.getItem(RBOLD); if(s1) saved={mode:"ajuste", snap:JSON.parse(s1), free:{}}; } }
  if(saved) rbRestore(saved); }catch(_){ }

// ---------- Ordenar páginas + selección múltiple + auto-scroll (1.27) ----------
let poOrder=null, poDragI=-1; const poThumbs={};
function openPoBoard(){ run(async()=>{ await need();
  if(pages<2){ status("Este PDF tiene una sola página: no hay orden que cambiar.",false); return; }
  poOrder=Array.from({length:pages},(_,k)=>k); renderPoBoard(); $("poDlg").style.display="flex"; }); }
$("bOrder").onclick=openPoBoard;
function renderPoBoard(){ const box=$("poGrid"); if(!box||!poOrder)return; box.innerHTML="";
  const n=poOrder.length; const cols=Math.max(1,Math.min(6,Math.round(Math.sqrt(n*1.9))));
  box.style.gridTemplateColumns="repeat("+cols+",1fr)"; box.style.gridAutoRows="minmax(118px,auto)";
  poOrder.forEach((pg,si)=>{ const card=document.createElement("div"); card.className="mgcard"; card.draggable=true;
    const th=poThumbs[pg];
    card.innerHTML="<div style='height:62px;display:flex;align-items:center;justify-content:center'>"+(th?("<img src='data:image/png;base64,"+th+"' style='max-height:60px;max-width:92%;border-radius:4px;box-shadow:0 1px 5px rgba(15,23,42,.25)'>"):"<div style='font-size:17px'>📄</div>")+"</div><div style='font-size:12px;font-weight:700'>Página "+(pg+1)+"</div><div style='font-size:11px;color:var(--mut)'>posición "+(si+1)+"</div>";
    card.addEventListener("dragstart",e=>{ poDragI=si; card.classList.add("drag"); try{ e.dataTransfer.setData("text/plain",String(si)); }catch(_){ } });
    card.addEventListener("dragend",()=>card.classList.remove("drag"));
    card.addEventListener("dragover",e=>e.preventDefault());
    card.addEventListener("drop",e=>{ e.preventDefault(); if(poDragI<0||poDragI===si)return; const mv=poOrder.splice(poDragI,1)[0]; poOrder.splice(si,0,mv); poDragI=-1; renderPoBoard(); });
    box.appendChild(card);
    if(!th && curDocId){ call("/api/render",{doc_id:curDocId,page:pg,zoom:0.16,password:docPw}).then(j=>{ poThumbs[pg]=j.png;
      if($("poDlg").style.display!=="none" && card.isConnected){ const d=card.querySelector("div"); if(d) d.innerHTML="<img src='data:image/png;base64,"+j.png+"' style='max-height:60px;max-width:92%;border-radius:4px;box-shadow:0 1px 5px rgba(15,23,42,.25)'>"; } }).catch(()=>{ }); } }); }
$("poCancel").onclick=()=>{ $("poDlg").style.display="none"; poOrder=null; };
$("poReset").onclick=()=>{ if(!poOrder)return; poOrder=Array.from({length:pages},(_,k)=>k); renderPoBoard(); };
$("poOk").onclick=()=>run(async()=>{ if(!poOrder)return;
  const same=poOrder.every((v,i)=>v===i);
  $("poDlg").style.display="none";
  if(same){ status("El orden quedó igual que estaba."); poOrder=null; return; }
  const old=page;
  const j=await callLong("/api/reorder",{doc_id:curDocId,order:poOrder,light:1},"Reordenar las páginas");
  if(!j||(!j.doc_id&&!j.pdf))throw new Error("El reorden no devolvió un documento: inténtalo de nuevo.");
  const ni=poOrder.indexOf(old); poOrder=null; thSel.clear();
  await adopt(j,curName,false);
  if(ni>=0)gotoPage(ni,false);
  status("Páginas reordenadas ✔"); });

let thSel=new Set(), thAnchor=null;
function paintThSel(){ document.querySelectorAll("#thumbList .titem").forEach(w=>{ w.classList.toggle("sel", thSel.has(+w.dataset.idx)); }); }
$("thumbList").addEventListener("click",e=>{ const w=e.target.closest?e.target.closest(".titem"):null; if(!w)return;
  const idx=+w.dataset.idx;
  if(e.ctrlKey||e.metaKey){ e.preventDefault(); e.stopPropagation(); if(thSel.has(idx))thSel.delete(idx); else thSel.add(idx); thAnchor=idx; paintThSel(); }
  else if(e.shiftKey&&thAnchor!==null){ e.preventDefault(); e.stopPropagation(); const a=Math.min(thAnchor,idx), b=Math.max(thAnchor,idx); for(let k=a;k<=b;k++)thSel.add(k); paintThSel(); }
  else { thSel.clear(); thSel.add(idx); thAnchor=idx; paintThSel(); } },true);

let thDragInfo=null;
$("thumbList").addEventListener("dragstart",e=>{ const w=e.target.closest?e.target.closest(".titem"):null; if(!w)return;
  const idx=+w.dataset.idx; thDragInfo={from:idx, multi:thSel.has(idx)&&thSel.size>1}; },true);
$("thumbList").addEventListener("dragend",()=>{ thDragInfo=null; },true);
$("thumbList").addEventListener("drop",e=>{ const w=e.target.closest?e.target.closest(".titem"):null;
  if(!w||!thDragInfo||!thDragInfo.multi)return;
  e.preventDefault(); e.stopPropagation();
  const to=+w.dataset.idx; thDragInfo=null;
  if(thSel.has(to))return;
  const moving=[...thSel].sort((a,b)=>a-b);
  const rest=Array.from({length:pages},(_,k)=>k).filter(x=>!thSel.has(x));
  let p;
  if(Math.min(...moving)<to) p=rest.indexOf(to)+1; else p=rest.indexOf(to);
  if(p<0)p=rest.length;
  const order=[...rest.slice(0,p),...moving,...rest.slice(p)];
  run(async()=>{ const j=await callLong("/api/reorder",{doc_id:curDocId,order:order,light:1},"Mover las páginas");
    if(!j||(!j.doc_id&&!j.pdf))throw new Error("El movimiento no devolvió un documento: inténtalo de nuevo.");
    thSel=new Set(moving.map((_,k)=>p+k));
    await adopt(j,curName,true); page=p; gotoPage(p,false); paintThSel();
    status(moving.length+" páginas movidas juntas a la posición "+(p+1)+" ✔"); }); },true);
// auto-scroll: al arrastrar cerca del borde, el panel se desplaza solo
let dragScrollEl=null, dragPtrY=0, dragScrolling=false;
function closestScroller(el){ while(el&&el!==document.body){ const s=getComputedStyle(el); if((s.overflowY==="auto"||s.overflowY==="scroll")&&el.scrollHeight>el.clientHeight+4) return el; el=el.parentElement; } return null; }
document.addEventListener("dragstart",()=>{ if(!dragScrolling){ dragScrolling=true; dragScrollEl=null; requestAnimationFrame(dragScrollTick); } },true);
document.addEventListener("dragover",e=>{ dragPtrY=e.clientY; dragScrollEl=closestScroller(e.target); },true);
function dragScrollTick(){ if(!dragScrolling)return;
  if(dragScrollEl){ const r=dragScrollEl.getBoundingClientRect(); const Z=56, MAX=16;
    if(dragPtrY<r.top+Z&&dragPtrY>=r.top-12){ dragScrollEl.scrollTop-=Math.max(2,Math.round(MAX*(1-Math.max(0,dragPtrY-r.top)/Z))); }
    else if(dragPtrY>r.bottom-Z&&dragPtrY<=r.bottom+12){ dragScrollEl.scrollTop+=Math.max(2,Math.round(MAX*(1-Math.max(0,r.bottom-dragPtrY)/Z))); } }
  requestAnimationFrame(dragScrollTick); }
document.addEventListener("dragend",()=>{ dragScrolling=false; dragScrollEl=null; },true);
document.addEventListener("drop",()=>{ dragScrolling=false; dragScrollEl=null; },true);

let rotDeg=90;
function openRotDlg(deg){ run(async()=>{ await need(); rotDeg=deg;
  $("rotTitle").textContent=deg<0?"Girar −90°":"Girar +90°";
  $("rotFrom").value=1; $("rotTo").value=pages; $("rotFrom").max=pages; $("rotTo").max=pages;
  document.querySelector('input[name="rotScope"][value="all"]').checked=true;
  $("rotInfo").textContent="El documento tiene "+pages+" páginas.";
  $("rotDlg").style.display="flex"; }); }
$("rotCancel").onclick=()=>{ $("rotDlg").style.display="none"; };
$("rotOk").onclick=()=>run(async()=>{ const sc=document.querySelector('input[name="rotScope"]:checked').value;
  let spec="";
  if(sc==="range"){ let a=parseInt($("rotFrom").value||"1",10), b=parseInt($("rotTo").value||"1",10);
    if(isNaN(a)||isNaN(b)||a<1||b<1||a>pages||b>pages) throw new Error("Revisa el rango: páginas entre 1 y "+pages+".");
    if(a>b){ const t2=a; a=b; b=t2; }
    spec=a+"-"+b; }
  $("rotDlg").style.display="none";
  const j=await call("/api/rotate",{pdf:cur,pages:spec,degrees:rotDeg});
  await adopt(j,curName,true);
  status(spec?("Páginas "+spec+" giradas ✔"):"Todo el documento girado ✔"); });
</script></body></html>
"""
