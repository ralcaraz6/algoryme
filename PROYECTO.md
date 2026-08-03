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
5. **Qué te cuesta hoy** (`#coste`, claves `calc.*`) — calculadora de coste del trabajo manual: tres
   deslizadores (horas/semana, coste/hora, % mecánico) y una tarjeta en tinta con el resultado.
   Fórmula: horas x 52 x coste, por el porcentaje mecánico; las semanas salen dividiendo entre 40 h.
   **Solo se ve en escritorio** (`@media (max-width:900px){.calc-sec{display:none}}`): en móvil los
   tres controles y la tabla no caben sin romperse, y se decidió ocultarla antes que degradarla.
   `renderCalc()` se llama también desde `applyI18n()` para que los números se reformateen al cambiar
   de idioma (es-ES usa punto de millar y coma decimal; en-GB al revés). No afirma ahorros: calcula
   lo que el visitante ya paga, y el aviso de debajo dice qué no incluye la cifra.
6. **FAQ** y **contacto**, sin cambios.

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

**El cubo del logo parpadea al entrar y luego se queda fijo**: `@keyframes lw-blink`, 1,06 s, corte
seco sin desvanecido y **tres repeticiones** (3,2 s). Al terminar vuelve a su estado base, que es
visible, así que no hace falta `animation-fill-mode`. Está en la cabecera y en el pie de las páginas
con marca y se para con `prefers-reduced-motion`. Dos decisiones del cliente que no conviene
deshacer: el corte es seco (descartó el desvanecido suave) y **no parpadea toda la visita**, solo da
la bienvenida.

**Efectos de scroll** (ago-2026): la cabecera se encoge y proyecta sombra al bajar, una línea
sienna de 2 px marca el progreso de lectura, el hero de la home se desplaza y se desvanece con el
scroll, y las apariciones `.reveal` entran escalonadas entre hermanos. Todo se apaga con
`prefers-reduced-motion`. ⚠️ La cabecera **sigue sin poder llevar `backdrop-filter`** (rompe el
menú móvil, ver la nota en el CSS): si quieres más profundidad, usa sombra.

## 4b. SEO: lo hecho y lo que falta (ago-2026)

Auditoría externa recibida el 2-ago-2026. **No hay generador**: el sitio es HTML a mano, y la fuente
de verdad de los textos es `content.json` + el diccionario embebido en cada página. Los cambios se
propagan con scripts, nunca a mano (§8).

Hecho:

- **Metadatos**: los siete `<meta description>` de servicio estaban cortados con un *slice* a 180
  caracteres, varios a mitad de palabra. Reescritos a mano, 143-149 caracteres, frase cerrada y
  llamada a la acción. Titles con modificador. Todo en `content.json` (`meta.es/en.svcN`).
- **Señales locales**: Barcelona en el title de la home, en la descripción, en el pie de las 11
  páginas (`footer.location`) y en una línea de la sección de contacto (`contact.local`).
- **Schema**: un único bloque de organización con `@id: https://algoryme.com/#organization` en las 11
  páginas, tipo `["ProfessionalService","LocalBusiness"]`, con `sameAs`, `knowsAbout`, `founder`,
  `priceRange` y `areaServed` con Barcelona. Antes la home tenía el bloque más pobre del sitio.
- **Canibalización entre servicios**: el bloque «Otros servicios» repetía la descripción completa de
  tres servicios (~150 palabras duplicadas por página). Ahora lista los seis restantes con solo el
  nombre (`.svc-others`).
- **Enlaces internos**: `index.html` → `/`, que es lo que dice el canonical.
- **Sitemap**: fuera `<priority>`; `lastmod` sale de la fecha real de git.
- **Imágenes**: las capturas de casos en WebP con respaldo JPG (200 KB → 84 KB) y `alt` descriptivo.

**La web inglesa ya existe de verdad (2-ago-2026).** `/en/` son ocho ficheros propios generados por
`scripts/build_en.py` a partir de las páginas españolas: traduce el texto horneado leyendo los
`data-i18n*` contra `content.json`, reescribe cabecera, JSON-LD, enlaces y recursos, y fija el idioma
de la página. **Tras cualquier cambio en el HTML español hay que volver a ejecutarlo**, o el inglés se
queda atrás:

    python3 scripts/build_en.py

Reglas que trae ese cambio y conviene no romper:

- El idioma lo manda la URL. `var lang` ya no se decide por navegador ni por `localStorage`, y el
  detector de idioma del navegador se retiró: con dos URLs reales, redirigir solo, aunque fuera por
  JavaScript, arriesga que Google indexe la home española como si fuera inglesa.
- El selector ES/EN **navega** usando `ALT_URL`, que va junto a `PAGE_META` en cada página.
- `?lang=en` sobre una página española redirige a su equivalente inglesa, para no romper enlaces viejos.
- `legal.html` y `privacidad.html` no tienen versión inglesa: su texto es jurídico y no está traducido.
  Las páginas inglesas enlazan a la española.
- Lo que no lleva `data-i18n` (el aviso sin JavaScript, `aria-label` del calendario y del menú, el alt
  de la imagen social) se traduce con la lista `LITERALES` del script. Si añades texto suelto en
  español, acuérdate de esa lista.

Pendiente, por orden de impacto:

1. **Contenido único por página de servicio** (900-1.200 palabras, FAQ propias con su `FAQPage`).
   Necesita datos que no tenemos: horquillas de precio reales, integraciones concretas y un caso.
   No inventarlos (§5).
2. **Ficha por caso**, página «quién está detrás», landing local y guía de precios.
3. **Google Business Profile**: la dirección y las coordenadas ya están en el schema
   (Carrer de Benet Mateu 44, 08034 Barcelona). Falta darse de alta y añadir el perfil a `sameAs`.

No tocar: bajar pesos de fuente. Se comprobó que Sora 600 e IBM Plex Mono 600 sí se usan.

## 4c. Accesibilidad y robustez (auditoría de ago-2026)

- **La página ya no depende de que el JavaScript arranque.** `.reveal` empieza oculto **solo** si el
  `<head>` ha podido marcar `document.documentElement.classList.add('js')`. Si el bundle falla, todo
  se ve. Además hay `@media (scripting: none)`. Si tocas el reveal, mantén las dos redes.
- **Las tipografías son nuestras** (`fonts/`, 12 ficheros woff2, 171 KB, subconjuntos latin y
  latin-ext), con `font-display:swap` y `preload` de las tres críticas. Ni una petición a Google:
  además de ser más rápido, era incoherente con el argumento de soberanía del dato que vende la web.
  Para actualizar una fuente, se baja el woff2 y se sustituye; no volver al `<link>` de Google.
- **Objetivos táctiles a 44 px**: selector de idioma, enlaces del menú, CTA de cabecera y, sobre todo,
  los deslizadores de la calculadora, que medían 4 px de alto (el área táctil de un `input[type=range]`
  es su caja, no el pomo). La pista se pinta con `::-webkit-slider-runnable-track` y `::-moz-range-track`.
- **Nada de texto por debajo de 12 px** y el `.kicker` sobre crema usa `--sienna-dark`.
- Los deslizadores anuncian unidades con `aria-valuetext` («28 € por hora», no «28»).
- Entrada de bloques a 320 ms con escalonado de 60 ms (antes 750 + 280).
- **El pie enlazaba a anclas**: sus cuatro servicios apuntan ya a su página, y dos de ellos compartían
  destino.

**Puntos de corte: cuatro y solo cuatro** — 560, 768, 1024 y 1280. Antes eran diez (400, 560, 720,
760, 820, 860, 880, 900, 1023, 1080), cinco de ellos apilados entre 760 y 900. Al unificar:

- el menú de escritorio aparece a partir de 1025 px, no de 901;
- las tarjetas de proyecto (`.webs`) ya no necesitan punto de corte propio: usan
  `repeat(auto-fit,minmax(260px,1fr))` y se reparten solas;
- la calculadora **se apila** entre 768 y 1024 en vez de desaparecer, y solo se retira por debajo
  de 768, que es donde de verdad no cabe.

Comprobado a 390, 560, 767, 768, 900, 1023, 1024, 1025, 1200 y 1440: sin desbordes horizontales.
Si añades una consulta de medios nueva, usa uno de los cuatro.

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
