# Algoryme — guía del proyecto

Documento de contexto para retomar el trabajo. Si eres una IA que empieza una sesión nueva,
**lee esto y `MARCA.md` antes de tocar nada**.

---

## 1. Qué es

**Algoryme** es la consultoría de inteligencia artificial de Rogelio Alcaraz. Diseña e implementa
agentes, automatizaciones y software a medida para empresas, con una promesa central que atraviesa
toda la comunicación: **todo se despliega en la infraestructura del cliente**. Sus datos, sus
modelos, su código, sin dependencia del proveedor.

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
- **Las capturas de pantalla del navegador integrado** dan tiempo de espera agotado con estas
  páginas. Alternativa que funciona: Chrome en modo headless
  (`--headless --screenshot --window-size=W,H`, y `--default-background-color=00000000` para
  transparencia).

### Formularios

Los 7 formularios envían por AJAX a FormSubmit. **El buzón de destino es privado y no coincide con
el email visible.** Al tocar emails, cambia solo lo visible y preserva los endpoints
`formsubmit.co/ajax/...`. Truco: sustituye el endpoint por un token antes de reemplazar y
restáuralo después, y comprueba que el número de endpoints no varía.

FormSubmit devuelve `200` con `success:false` cuando marca algo como spam, y `4xx` si el buzón no
está activado. **Hay que mirar la respuesta**, porque `fetch` solo rechaza ante fallo de red. Esto
ya está implementado; no lo quites.

## 4. Estructura de la home

El orden cuenta una historia de venta y no es casual:

1. **Hero** — el problema del cliente en una frase, con la promesa de infraestructura en negrita.
2. **El problema** — por qué casi ningún proyecto de IA llega a producción, con tres riesgos.
3. **Tu stack, no el nuestro** — la respuesta a ese problema. Es el diferencial de la marca.
4. **El trabajo interno** — cinco capacidades en una lista seleccionable con panel de vista previa.
5. **Integraciones** — una sola fila de logos, alineada a la izquierda.
6. **Cómo trabajamos** — línea de tiempo de cinco pasos hasta producción.
7. **Casos de éxito** — ocho. Los tres primeros tienen página propia; los otros cinco son tarjetas
   compactas bajo el epígrafe «Otros sistemas en producción», con sector, título y resumen.
8. **El equipo** y **el fundador**.
9. **FAQ**, **CTA de reserva** y **contacto**.

Páginas aparte: `casos.html` + 3 fichas de caso, `herramientas.html`, `formacion.html` + 4 cursos,
el embudo del curso gratuito (3 páginas), `newsletter.html`, `legal.html`, `privacidad.html`, `404.html`.

`herramientas.html` enlaza a **Rachea** y **Prospéctalo**, los dos productos de suscripción. Su
código está en otros repositorios; el contexto para trabajar en ellos está en
**[HERRAMIENTAS.md](HERRAMIENTAS.md)**.

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

En julio de 2026 el cliente aportó cinco proyectos más. Se añadieron **solo como tarjeta** (sector,
título y resumen), sin página propia: de ellos se sabe qué hacen y para qué sector, pero no la
situación de partida, el resultado ni el stack, y rellenar esos campos habría sido inventarlos.
Cuando lleguen los detalles reales de alguno, ascenderlo a página completa es rellenar `situation`,
`built`, `how`, `outcome` y `stack` en su entrada de `content.json` y clonar una ficha existente.

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
