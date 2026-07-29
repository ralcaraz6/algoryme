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

Sitio **estático sin compilación**. 18 páginas HTML, cada una autocontenida: su CSS en línea, su
JavaScript en línea y el diccionario de textos embebido. La única petición externa son las fuentes
de Google. Se despliega solo con hacer *push* a `main`.

### El motor de idiomas

`content.json` es la fuente de la verdad de todos los textos, en español e inglés. Pero **en cada
página va embebido, minificado, en una sola línea**: `var CONTENT = {...};`. El HTML lleva atributos
`data-i18n` y el texto español "horneado" dentro, para que los buscadores y los navegadores sin
JavaScript vean contenido real.

Esto significa que **al cambiar un texto hay que hacer tres cosas**: editar `content.json`,
re-embeber el diccionario en las 18 páginas y re-hornear el texto estático. Hay un script para eso
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
- **Los `curl` en bucle** desde el entorno de Claude se topan con límites de red y devuelven vacío.
  Para verificar en producción, usa el navegador o fija una IP con `--resolve`.
- **Las transiciones CSS quedan congeladas** en Chrome headless con `--virtual-time-budget`: al
  medir con `getComputedStyle` justo después de un clic devuelve el valor *inicial*, no el final,
  y parece que la regla no se aplica. Antes de dar por roto un estado (`.open`, `:hover`), inyecta
  `*{transition:none!important}` y vuelve a medir. Pasó con el icono +/− del índice de proyectos.
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

**Consentimiento:** se retiró la casilla «He leído y acepto la política de privacidad», también a
petición del cliente. En su lugar queda un aviso permanente bajo el formulario con enlace a la
política. Es una decisión suya y está tomada a conciencia; si algún día un asesor legal pide volver
a la casilla marcable, el patrón anterior era un `input[type=checkbox]` obligatorio validado en el
`submit`.

## 4. Estructura de la home

El orden cuenta una historia de venta y no es casual (recortado en jul-2026 a petición del cliente,
para que la home sea más corta y directa):

1. **Hero** — el problema del cliente en una frase, con la promesa de infraestructura en negrita.
   El copy va **centrado** (una sola columna, `.hero-copy`) y debajo, **a ancho completo**, la
   banda `.hero-band`: el titular `heroPanel.lead` en mayúsculas («NOS ENCARGAMOS DE TODO») y un
   marquee (`.hb-marquee`/`.hb-track`) que desfila de izquierda a derecha `heroPanel.items`
   (informes, facturas, CRM...), «todo lo que hacemos». Evolución del feedback de una amiga de Roge
   (jul-2026): se quitó la tarjeta blanca de la derecha, se movió la barra debajo del welcome copy,
   se pasó a mayúsculas y a primera persona («se encarga» → «nos encargamos»). ⚠️ **Los items del
   track se pintan dos veces** (el segundo grupo con `.hb-dup aria-hidden`) para que el bucle cierre
   sin salto: la animación `hb-run` mueve el track de `-50%` a `0`, así que las dos mitades tienen
   que ser idénticas. Cada item es su clave i18n (`heroPanel.items.N`) y funciona igual en inglés
   (las mayúsculas son `text-transform`, no van en el texto). El texto accesible va en `#hpAlt`
   (sr-only) porque el marquee es decorativo; con `prefers-reduced-motion` el track se para y se
   envuelve.
2. **Servicios** — **seis** capacidades en una lista seleccionable con panel de vista previa
   (`backoffice.items`). Es la sección a la que apunta **Servicios** en la navegación
   (`#aplicaciones`); si le cambias el `id`, se rompe el enlace en las 18 páginas. El kicker dice
   «Servicios»; antes decía «El trabajo interno». El panel se rellena por JS desde `backoffice.items.N`
   (nombre, tagline, bullets, icono clonado de la pestaña): para añadir un servicio hay que crear el
   `<li>` con su `data-bo="N"` **y** la entrada N en `content.json`. La sexta, «Aplicaciones y webs
   a medida», se añadió en jul-2026 porque es de lo que más pregunta la gente.
3. **Cómo trabajamos** — línea de tiempo de cinco pasos hasta producción.
4. **Proyectos** — tres tarjetas ilustradas y un botón a `casos.html`. La home enseña una
   muestra, no el catálogo: si crece aquí, la página se hace interminable. El trío destacado
   (índices 0-2 de `cases.items`) es **inmobiliario, finanzas y producción**: en jul-2026 el 3º pasó
   de «renta variable» (mercados) a «transportista más barato» para no duplicar el sesgo financiero;
   renta variable bajó al índice 3 y conserva su ficha (`caso-analisis-renta-variable.html`, ahora
   `PAGE_META = 'caso3'`). ⚠️ Las ilustraciones de tarjeta y el `PAGE_META`/`data-i18n` de cada ficha
   van **atados al índice**: si reordenas `cases.items`, hay que renumerar las fichas y sus enlaces.
5. **El equipo** y **el fundador**.
6. **FAQ** y **contacto**. El contacto es **un solo panel**: formulario a la izquierda y las tres
   vías (llamada, WhatsApp, email) a la derecha, dentro del mismo marco. La reserva de llamada de 30
   minutos vive aquí (columna derecha) y en el header; no hay una sección de reserva aparte.

**Secciones que existieron y se quitaron** (su CSS puede seguir presente, inofensivo): «El problema»
(los tres riesgos del 95%), «Tu stack, no el nuestro» (`band-own`, el diferencial de propiedad;
retirada en jul-2026), «Integraciones» (la fila de logos) y el **CTA de reserva** independiente
(el `band-cta` con el formulario «Prefieres email» / `emailCapture`). El JS del `emailCapture` sigue
en las páginas pero está protegido con `if (capForm)`, así que no hace nada al faltar el markup.

Páginas aparte: `casos.html` + 4 fichas de caso, `herramientas.html`, `formacion.html` + 4 cursos,
el embudo del curso gratuito (3 páginas), `newsletter.html`, `legal.html`, `privacidad.html`, `404.html`.

`herramientas.html` enlaza a **Rachea** y **Prospéctalo**, los dos productos de suscripción. Su
código está en otros repositorios; el contexto para trabajar en ellos está en
**[HERRAMIENTAS.md](HERRAMIENTAS.md)**.

### Proyectos (antes «Casos de éxito»)

En julio de 2026 el cliente los renombró a **Proyectos**. El cambio es solo de etiqueta: los
ficheros siguen llamándose `casos.html` y `caso-*.html`, y las claves de `content.json` siguen
siendo `cases`, `casesPage` y `caseDetail`. **No renombres los ficheros**: las URLs están indexadas
y no hay redirecciones montadas.

Cada proyecto se cuenta con tres bloques fijos —**El problema**, **La solución**, **El resultado**—
tanto en el índice desplegable de `casos.html` como en las fichas completas. Las etiquetas viven en
`cases.labels`.

**Cuatro de los ocho proyectos no tienen resultado publicado**, y es deliberado: de ellos se conoce
el problema y la solución, pero no el resultado medido, y la regla dura prohíbe inventarlo. El
bloque «El resultado» solo se pinta si el proyecto tiene `outcome`; los que no lo tienen sencillamente
no lo muestran, sin hueco ni texto de relleno. Cuando el cliente aporte los resultados reales, basta
con rellenar `outcome` en su entrada de `content.json`.

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
- Los cambios de marca y de contenido se propagan a 18 páginas. Hazlo siempre con un script y
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
