# Aven PDF

Editor de PDF gratuito para Windows, 100 % sin conexión: ver, unir, dividir,
reordenar, girar y borrar páginas; convertir a Word, Excel, imágenes y texto;
OCR en español; marca de agua, sellos, cifrado y firma digital con certificado.
Interfaz en español, estilo lector clásico, en su propia ventana de programa.

## Instalación

Descarga `AvenPDF_Setup.exe` desde la página de **Releases** de este
repositorio y ejecútalo. No necesita internet, ni Python, ni permisos de
administrador. Funciona en Windows 10 y 11 (64 bits).

## Privacidad

Aven PDF trabaja completamente en tu computadora. Ningún documento sale de
tu equipo: no hay servidores, ni cuentas, ni telemetría. Detalles en
[PRIVACY.md](PRIVACY.md).

## Cómo se construye

El instalador se compila automáticamente con GitHub Actions
(`.github/workflows/build-installer.yml`): descarga el Python oficial
incrustado y las librerías abiertas (PyMuPDF, pypdf, pdf2docx, RapidOCR,
pywebview, entre otras), arma el paquete y lo empaqueta con Inno Setup.

## Firma de código (Code signing policy)

Los binarios oficiales de este proyecto se firman digitalmente para que
Windows los reconozca como seguros. Free code signing provided by
[SignPath.io](https://signpath.io), certificate by
[SignPath Foundation](https://signpath.org). Solo son oficiales los
instaladores publicados en los Releases de este repositorio y firmados
a partir de compilaciones públicas de este código.

## Licencia

Código propio bajo licencia MIT (ver [LICENSE](LICENSE)). Las librerías
incluidas conservan sus propias licencias abiertas (PSF, MIT, Apache-2.0,
AGPL-3.0 para PyMuPDF, entre otras).
