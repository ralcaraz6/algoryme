# Algoryme — guía del proyecto

Documento de contexto para retomar el trabajo. Si eres una IA que empieza una sesión nueva,
**lee esto y `MARCA.md` antes de tocar nada**.

---

## 1. Qué es

**Algoryme** desarrolla software a medida para empresas: sistemas, automatizaciones y agentes que
les hacen **ganar más o gastar menos**. Posicionamiento premium orientado a resultado de negocio
(reenfocado en jul-2026 desde «consultoría de IA»: la IA es el medio, no el producto). Promesa
central que atraviesa toda la comunicación: **todo se despliega en la infraestructura del cliente**,
en producción, no en demos. Sus datos, sus modelos, su código, sin dependencia del proveedor.

**Regla de posicionamiento:** premium se construye con verdad, no con cifras inventadas. Nunca
números de resultados de clientes sin fuente ni permiso (ver la regla dura, §5). Las palancas premium
son reales: autoridad (años con datos, plataformas con millones de usuarios), «producción no demos»,
riesgo compartido (diagnóstico primero) y escasez (pocos proyectos a la vez).

Equipo de seis personas. No es una agencia grande y la web no debe fingir que lo es.

La marca se llamó antes **Action Labs** (hasta el 27-jul-2026) y antes **50 Labs**. Los repositorios
antiguos siguen vivos y solo redirigen; no los borres.

## 2. Dónde está todo

| Qué | Dónde |
|---|---|
| Código | `/Users/rogelio/tt/algoryme` |
| Repositorio | `github.com/ralcaraz6/algoryme` (público) |
| Web en producción | **https://algoryme.com** (GitHub Pages, HTTPS forzado) |
| Vista previa local | configuración `algoryme` en `.claude/launch.json`, puerto **5098** |
| Textos | `content.json` (ES/EN) |
| Marca | `marca/` + `MARCA.md` |
| Repositorio antiguo | `ralcaraz6/action-labs` — solo redirecciones, no borrar |

**Correo:** `info@algoryme.com` en Google Workspace. DNS en Namecheap (BasicDNS). SPF, DKIM y DMARC
configurados y verificados los tres en `PASS`.

## 3. Cómo está construido

Sitio **estático sin compilación**. 19 páginas HTML, cada una autocontenida: su CSS en línea, su
JavaScript en línea y el diccionario de textos embebido. La única petición externa son las fuentes
de Google. Se despliega solo con hacer *push* a `main`.

### El motor de idiomas

`content.json` es la fuente de la verdad de todos los textos, en español e inglés. Pero **en cada
página va embebido, minificado, en una sola línea**: `var CONTENT = {...};`. El HTML lleva atributos
`data-i18n` y el texto español "horneado" dentro, para que los buscadores y los navegadores sin
JavaScript vean contenido real.

Esto significa que **al cambiar un texto hay que hacer tres cosas**: editar `content.json`,
re-embeber el diccionario en las 19 páginas y re-hornear el texto estático. Hay un script para eso
en el histórico de la sesión; si no lo tienes, es un recorrido con un parser de llaves balanceadas
(el diccionario está minificado, las expresiones regulares ingenuas fallan en silencio).

### Trampas conocidas, todas encontradas a base de romperlas

- **`applyI18n()` hace `el.textContent = v`** sobre todo `[data-i18n]`, así que **destruye cualquier
  hijo HTML**. Si un texto lleva un enlace dentro, el `<a>` va *fuera* del nodo traducido. Pasó una
  vez y el enlace a la política de privacidad desapareció de toda la web.
- **`content.json` se desincroniza.** Una sesión editó el diccionario embebido de una página y no el
  fichero. Antes de regenerar nada, **compara el embebido de cada página con `content.json`** o
  revertirás cambios ajenos.
- **Las páginas se crean clonando una hermana**, así que heredan `og:url`, `hreflang` y el
  `BreadcrumbList` de la plantilla. Hay que reescribir esos tres a mano en cada página nueva.
- **`applyI18n()` necesita `var PAGE_META`** declarado arriba del script (bloque *PAGE CONFIG*).
  Si falta, la función revienta en su primera línea y **la página se queda en español para
  siempre**: no traduce nada, ni textos ni `<title>`. Pasó con la migración de la home de ago-2026,
  que se llevó por delante el bloque en la home y en las siete landings de servicio, y no se vio
  porque el español "horneado" en el HTML tapa el fallo. Si tocas el idioma, mira la consola.
- **Los `curl` en bucle** desde el entorno de Claude se topan con límites de red y devuelven vacío.
  Para verificar en producción, usa el navegador o fija una IP con `--resolve`.
- **Las transiciones CSS quedan congeladas** en Chrome headless con `--virtual-time-budget`: al
  medir con `getComputedStyle` justo después de un clic devuelve el valor *inicial*, no el final,
  y parece que la regla no se aplica. Antes de dar por roto un estado (`.open`, `:hover`), inyecta
  `*{transition:none!important}` y vuelve a medir. Pasó con el icono +/− del índice de proyectos.
- **Una regla suelta de `font-size` puede aplastar toda la escala.** En jul-2026 la home llevaba
  `h1,h2,.founder-title,.hero h1{font-size:clamp(1.85rem,2.9vw,2.3rem)}` colada **dentro del bloque
  de `text-wrap`**, fuera de cualquier media query. Igualaba h1 y h2 (36,8 px los dos a 1440) y
  dejaba el titular de la home un 38 % más pequeño que el de las demás páginas, que sí llegaban a
  59,2 px. Lo detectó el cliente a ojo, no nosotros. **Antes de publicar cambios de estilo, pasa
  `scripts/check-maqueta.html`** (instrucciones dentro): mide jerarquía, tamaños de sección,
  texto diminuto, desbordes y cortes de línea en las 19 páginas a 1440/1024/390.
- **Las capturas de pantalla del navegador integrado** dan tiempo de espera agotado con estas
  páginas. Alternativa que funciona: Chrome en modo headless
  (`--headless --screenshot --window-size=W,H`, y `--default-background-color=00000000` para
  transparencia).

### Formularios

Los 7 formularios y la reserva de llamada envían por AJAX a FormSubmit. Desde julio de 2026 el
buzón de destino es **`info@algoryme.com`**, el mismo que se muestra en la web (antes iba a una
gmail personal). Están en 19 sitios: la constante `ENDPOINT` de cada una de las 18 páginas, más un
`fetch` con la dirección escrita a mano en `curso-tareas-claude-registro.html`. Si vuelves a
cambiar de buzón, no basta con la constante: busca `formsubmit.co/ajax/` y cuenta 19.

**Cambiar el buzón no basta con tocar el código.** FormSubmit no entrega a una dirección nueva
hasta que alguien confirma desde ella: el primer envío devuelve error y dispara un correo de
activación al buzón de destino. Hasta que se pulsa ese enlace, **todos los formularios fallan en
producción**. El orden correcto es desplegar, enviar un formulario cualquiera y activar en el
minuto siguiente. Desde el entorno de Claude no se puede disparar: el proxy bloquea la salida a
`formsubmit.co`.

FormSubmit devuelve `200` con `success:false` cuando marca algo como spam, y `4xx` si el buzón no
está activado. **Hay que mirar la respuesta**, porque `fetch` solo rechaza ante fallo de red. Esto
ya está implementado; no lo quites.

**El formulario de contacto pide cuatro cosas**: nombre, email, teléfono (opcional) y mensaje.
Empresa y «qué te interesa» se quitaron en julio de 2026 por petición del cliente, para bajar la
fricción. El modal de reserva de llamada pide nombre, email, teléfono (opcional) y mensaje — la **empresa se
quitó en jul-2026** (antes era obligatoria). El botón que abre el modal en el header dice **«Agendar
llamada»** (`ui.bookShort`); el CTA descriptivo «Reserva una llamada de 30 minutos» (`ui.bookCta`)
se mantiene en el hero y otros sitios.

**Estados del formulario de contacto (ago-2026):** los errores de campo salen **debajo de su campo**
(`.field-err`, `#err-name` y `#err-email`), no en el aviso global. El aviso global `#formError` queda
solo para fallo de red o de servidor. El mensaje de email cambia según el motivo (vacío o mal
formado) reescribiendo su `data-i18n`, para que siga traduciéndose al cambiar de idioma. El botón se
deshabilita mientras envía y el error de campo desaparece al corregirlo.

**Etiquetas de llamada unificadas (ago-2026):** menú «Reservar llamada» (`ui.bookShort`), hero y
bandas CTA «Reservar 30 minutos de diagnóstico» (`hero.cta1`, `ui.bookCta`), contacto «Reservar 30
minutos», formulario «Enviar mi caso», WhatsApp «Escribir por WhatsApp», email «Escribir un email».
No volver a introducir «Agendar llamada» ni «Reservar» a secas.

**Consentimiento:** se retiró la casilla «He leído y acepto la política de privacidad», también a
petición del cliente. En su lugar queda un aviso permanente bajo el formulario con enlace a la
política. Es una decisión suya y está tomada a conciencia; si algún día un asesor legal pide volver
a la casilla marcable, el patrón anterior era un `input[type=checkbox]` obligatorio validado en el
`submit`.

## 4. Estructura de la home

Rehecha en ago-2026 con el diseño que se probó en el repositorio `algoryme-v2`. El orden es:

1. **Hero** — «Construimos el software que hace crecer tu negocio», copy centrado y un solo CTA.
2. **Servicios** (`#aplicaciones`, claves `svc.*`) — **siete servicios agrupados en tres familias**
   (Construimos, Automatizamos, Analizamos), con la **auditoría destacada** arriba como puerta de
   entrada. Cada tarjeta lleva «Leer más» a su propia landing `servicio-<slug>.html`.
   ⚠️ El nombre de clase `.svc-ico` ya está cogido por el icono grande del hero de las landings;
   las tarjetas usan `.card-ico` / `.card-icobox`.
3. **Proyectos** (`#casos`) — tres previews reales de web (prospectalo.com, app.svinvesting.com,
   noemisarpe.com) en un marco de navegador, con degradado abajo para que la captura no corte a media
   frase. Las capturas están en `casos/` y se generaron con un servicio externo; para actualizarlas,
   vuelve a capturarlas y sustituye el JPG.
4. **Cómo trabajamos** — la línea de tiempo de cinco pasos.
5. **FAQ** y **contacto**, sin cambios.

**La sección de equipo ya no existe.** Salió de la home a `equipo.html` el 1-ago-2026 y ese mismo
día el cliente pidió retirarla del todo: fuera la pestaña del menú y el enlace del pie, fuera del
sitemap, y `equipo.html` como redirección con `noindex, follow`. Los textos (`team.*` de
`content.json`), los retratos de `equipo/` y el script `equipo/uniformar.py` siguen en el
repositorio; recuperarla es rescatar el `<main>` del commit anterior a la retirada.

**Secciones retiradas en la migración**: «El problema», «Tu stack, no el nuestro», «Integraciones»,
el CTA de reserva suelto, el selector «¿Qué le está robando el tiempo a tu equipo?», la comparativa
«Algoryme frente a otros» y la sección «El fundador» (fusionada en Equipo).

**Páginas retiradas**: formación (5), herramientas, fichas de proyecto (5), newsletter y el embudo
del curso gratuito (3). **No se borraron**: cada una quedó como redirección con `noindex, follow`
y su canonical, para no dar 404 ni perder el SEO acumulado. Si alguna vez se recuperan, el
contenido está en el historial de git.


## 4b. La página de equipo, las fotos y el idioma automático

**`equipo.html`** (ago-2026) es la única página que habla del equipo: Rogelio destacado arriba y
los cinco restantes en una rejilla centrada, cada uno con una descripción de una línea sacada de
`team.members[].bio`. ⚠️ Álvaro Entrena **no lleva enlace a LinkedIn** porque no tenemos su perfil;
el de los otros cuatro sí es real. No inventes uno.

**Las fotos del equipo se unifican con `equipo/uniformar.py`**: recorta el fondo original de cada
retrato, lo compone sobre el mismo fondo de marca, encuadra todas las cabezas al mismo tamaño y
aplica el mismo tratamiento de color. Los originales viven en `equipo/_src/` y no se tocan; la
salida es `equipo/<slug>.jpg` a 640×640. Necesita `rembg` en un entorno virtual (el script explica
cómo); la primera ejecución descarga un modelo de 176 MB. Si alguien manda una foto nueva, se deja
en `_src/` y se vuelve a ejecutar: es la manera de que las seis sigan pareciendo un mismo set.

**Idioma automático**: si el visitante no ha elegido idioma antes (ni `?lang=`, ni `localStorage`),
`detectLang()` mira `navigator.languages`. Cualquier variante de español —y también `ca-ES`,
`gl-ES`, `eu-ES`— sirve la web en español; cualquier otro idioma la sirve en inglés. Si no hay dato,
español. La elección manual del selector ES/EN se guarda y manda sobre la detección.

**El cubo del logo parpadea** como el cursor de una terminal esperando a que escribas
(`@keyframes lw-blink`, 1,06 s, corte seco sin desvanecido). Está en la cabecera y en el pie de las
12 páginas con marca, y se para con `prefers-reduced-motion`. Es decisión del cliente: si alguien
propone suavizarlo, era la alternativa que descartó.

**Efectos de scroll** (ago-2026): la cabecera se encoge y proyecta sombra al bajar, una línea
sienna de 2 px marca el progreso de lectura, el hero de la home se desplaza y se desvanece con el
scroll, y las apariciones `.reveal` entran escalonadas entre hermanos. Todo se apaga con
`prefers-reduced-motion`. ⚠️ La cabecera **sigue sin poder llevar `backdrop-filter`** (rompe el
menú móvil, ver la nota en el CSS): si quieres más profundidad, usa sombra.

## 5. La regla dura

> **Ningún dato, cliente, logo o métrica de esta web puede ser inventado. Si un dato no está
> verificado, se omite o se formula de manera cualitativa.**

Es la regla que más veces ha tenido que aplicarse, y a veces contra lo que se pedía en el momento:

- Se pidió presentar el "95% de proyectos de IA que fracasan" como experiencia propia. **No se hizo**:
  esa cifra es de un estudio del MIT y atribuírsela sería inventar. Se reescribió la sección en
  primera persona y sin cifra: *«¿Por qué casi ningún proyecto de IA llega a producción?»*.
- Se pidió que no pareciera que solo hay tres casos. **No se inventaron casos ni años de
  experiencia**. Lo que se hizo fue quitar todo lo que contaba (el «tres sistemas» del subtítulo, los
  KPIs, la línea «es una marca de Rogelio Alcaraz» del pie) y dar a los tres casos reales
  profundidad de página completa.

Si en el futuro hay más proyectos que contar, la estructura ya está montada: añadir un caso es
rellenar contenido en `content.json` y generar su página.

En julio de 2026 el cliente aportó cinco proyectos más, hasta ocho. De ellos se sabe qué hacen y
para qué sector, pero no la situación de partida, el resultado ni el stack, así que **no tienen
página propia**: rellenar esos campos habría sido inventarlos. Cuando lleguen los detalles reales de
alguno, ascenderlo es rellenar `situation`, `built`, `how`, `outcome` y `stack` en su entrada de
`content.json`, clonar una ficha existente y añadir el enlace en su fila del índice.

En ago-2026 el tercer ejemplo de web de la home pasó de `orph.eus` a `noemisarpe.com`. El cliente
**confirmó expresamente que esa web es obra suya**, que es lo que permite mantenerla bajo el título
«Esto ya está en producción». No la quites por dudar de la autoría: ya se preguntó y está respondida.

**Dónde vive cada cosa:** la home enseña tres casos y un botón; `casos.html` es el índice completo,
una fila por caso con «Ver más» que despliega en el sitio (`#casesList`, un abierto a la vez, mismo
patrón que las FAQ). Las tres filas con ficha añaden dentro «Ver el caso completo». Esta división
es deliberada y la pidió el cliente: la home no debe crecer con cada caso nuevo. Añadir un caso es
una entrada en `content.json` y una fila en `casos.html`; la home no se toca.

## 6. Verificación antes de publicar

Nada se despliega sin pasar esto. Está probado que hace falta:

1. **JavaScript**: extraer los `<script>` de cada página y pasarles `node --check`.
2. **JSON-LD**: parsear cada bloque `application/ld+json`.
3. **CSS**: comprobar que las llaves de cada `<style>` están balanceadas.
4. **Enlaces**: que ningún `href` interno apunte a un fichero inexistente.
5. **Diccionario**: que el embebido coincide exactamente con `content.json`.
6. **Maquetación**: un detector en navegador que, para cada página y en escritorio (1440 px) y móvil
   (390 px), busca texto sobredimensionado, desbordes horizontales y **textos que saltan de línea
   antes de llenar su contenedor**. Este último es un requisito explícito del cliente y ha cazado
   varios fallos reales.

## 7. Pendiente

- **El vídeo del curso gratuito** es un placeholder ajeno (un documental de Seiko). Está en
  `curso-tareas-claude-acceso.html`, variable `VIDEO_ID`. Cambiar antes de compartir el curso.
- **Las biografías del equipo**: las de las cinco personas que no son Rogelio describen el puesto,
  no su trayectoria. Faltan datos reales. No inventar.
- **DMARC**: está en `p=none` (solo observa). Subir a `p=quarantine` cuando lleve semanas sin
  incidencias.
- **Un cliente que autorice nombre y testimonio.** Es el mayor déficit de credibilidad de la web.

## 8. Cómo trabaja bien este proyecto

- El cliente revisa visualmente y con detalle. **Mira siempre el resultado con una captura antes de
  darlo por bueno**, no solo los números.
- Cuando algo no se puede hacer como se pide (porque sería inventar un dato o porque es un límite
  físico del formato), **decirlo en una frase y entregar la mejor alternativa**, no bloquear.
- Los cambios de marca y de contenido se propagan a 19 páginas. Hazlo siempre con un script y
  **verifica el número de sustituciones**, no a mano.

## 8b. Analítica y cookies

- **Google Analytics 4** (`G-G9NT4L51DD`) está en el `<head>` de las 19 páginas, justo tras el
  `<meta charset>`, con **Consent Mode v2**: por defecto `analytics_storage:'denied'`. No mide nada
  hasta que el visitante acepta.
- El **banner de cookies** (`#ckBanner`, clases `ck-*`) vive antes del `<script>` principal de cada
  página; sus textos son `cookie.*` en `content.json` (ES/EN). Guarda la decisión en `localStorage`
  bajo `algoryme-consent` (`granted`/`denied`); al aceptar hace `gtag('consent','update',...)`.
- Si algún día se quita GA, hay que **revertir la política de privacidad**: el apartado de cookies
  (estático en `privacidad.html` y en el dict `EXTRAS` de las 18 páginas) afirma que SÍ se usa
  Google Analytics con consentimiento. Ese texto es la fuente de verdad legal.

## 9. Autonomía

El cliente ha autorizado trabajar sin pedirle permiso paso a paso. En la práctica:

- **Commit y push directos a `main`.** No hace falta rama, ni PR, ni esperar visto bueno. `main`
  es producción: lo que entra sale publicado en algoryme.com.
- **Sin preguntar antes de mergear** ni antes de publicar un cambio ya pedido.
- **Cuidado con el push.** El repositorio se suele clonar con `HEAD` en una rama de trabajo, no en
  `main`. `git push origin main` empuja la `main` local —normalmente desactualizada— y responde
  `Everything up-to-date` sin subir nada. Usa `git push origin HEAD:main` y **comprueba el rango
  de commits** que imprime.
- Lo que sigue mereciendo un aviso, no por permiso sino porque el cliente querría enterarse:
  reescribir historia publicada (`push --force`), borrar trabajo sin fusionar, actuar fuera de
  este repositorio (correos, servicios externos) y publicar afirmaciones sobre la empresa que no
  se puedan verificar contra el código o contra un dato real. La regla de no inventar datos no la
  levanta ninguna autorización.
- La autonomía es para ejecutar, no para decidir por él. Si hay dos maneras razonables y la
  elección es de criterio suyo, se elige la más conservadora, se hace, y se dice cuál se eligió.
