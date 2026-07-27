# Algoryme — guía de marca

Todo lo de aquí está decidido y aplicado en producción. No lo reabras sin que lo pida Rogelio.

---

## 1. La idea

Algoryme hace que la IA llegue a producción en la infraestructura del propio cliente. La marca
tiene que sonar **técnica y sobria**, no a agencia de marketing ni a startup con hype.

El nombre junta **algo** (algoritmo, y en español «algo») con la terminación **-ryme**. El énfasis,
cuando haga falta, va en *algo*. Nunca en *ryme*, que no significa nada.

---

## 2. El logo

```
ALGORYME▌
```

**Wordmark en mayúsculas, Chivo 900, un solo color, con el cursor de bloque al final.**

- Nada de partir la palabra en dos tonos. Se probó y se descartó: destacar «ryme» no dice nada.
- El cursor es parte del logo, no un adorno pegado. Mide `0.5 em` de ancho por `0.9 em` de alto,
  con `0.15 em` de separación.

### Por qué Chivo

Las tipografías anteriores dejaban un hueco visible en la unión de la **Y**, que se leía como una
interrupción. Chivo 900 tiene el vértice bajo y los brazos gruesos, así que la unión queda maciza.
Es además la más compacta y contundente de las que se probaron.

### El monograma

Un **caret**: la A sin travesaño, que es a la vez la inicial y el símbolo de cursor (`^`, que en
programación se llama precisamente *caret*). Va en blanco sobre cuadrado siena.

Se usa solo cuando el espacio es muy pequeño o cuando el nombre ya aparece escrito al lado.

### Cuándo cada uno

| Situación | Qué usar |
|---|---|
| Cabecera, documentos, firma de correo | Wordmark en una línea |
| Avatar redondo (Workspace, LinkedIn) | Wordmark en una línea al **90 % del diámetro** |
| Favicon, o menos de 32 px | Caret |

> En un círculo, la línea horizontal centrada pasa por el diámetro, que es la parte más ancha.
> Por eso el wordmark entra al 90 % y no al 70 % del cuadrado inscrito. **Nunca lo apiles**
> en ALGO / RYME: se probó y se descartó.

### Aire mínimo

Deja alrededor del logo, como mínimo, el ancho del cursor de bloque.

---

## 3. Color

| Nombre | Hex | Para qué |
|---|---|---|
| **Tinta** | `#211D18` | Texto principal y el logo. Es un casi-negro cálido, **nunca negro puro**. |
| **Siena** | `#B5401C` | **Color de acción**: botones, enlaces, acentos, el cursor. |
| Siena oscuro | `#943216` | Estado *hover* de los botones. |
| **Papel** | `#FAF7F0` | Fondo de página. |
| **Crema** | `#F2ECDE` | Bandas de sección, para dar ritmo. |
| **Tarjeta** | `#FEFCF8` | Tarjetas, cabecera y paneles. |
| Apagado | `#6B6153` | Texto secundario. |
| Línea | `#E4DFD4` | Bordes y separadores. |
| Verde | `#31513F` | Uso muy puntual, viñetas. |

### Dos reglas de color que no se saltan

**Nada de blanco puro.** Ni `#FFFFFF` de fondo ni superficies brillantes. Fue una queja explícita:
el blanco puro sobre papel cálido rompe la sensación de calidad. La única excepción es el texto
sobre siena o sobre tinta.

**El siena es el color de acción, no el de la marca.** Por eso el logo va en tinta. Si algún día el
logo pasa a siena, el botón principal tiene que pasar a tinta, o el CTA deja de destacar y se pierde
la jerarquía de la cabecera.

### Contraste verificado

Todo cumple WCAG AA (mínimo 4,5):

- Tinta sobre tarjeta: **16,35**
- Apagado sobre tarjeta: **5,92**
- Siena sobre tarjeta: **5,52**
- Blanco sobre botón siena: **5,65**

---

## 4. Tipografía

| Uso | Fuente | Peso |
|---|---|---|
| Logo | **Chivo** | 900 |
| Titulares y texto | **Sora** | 400 / 600 / 700 |
| Datos, etiquetas, código | **IBM Plex Mono** | 500 / 600 |

La monoespaciada no es decorativa: marca lo que es dato o técnico (rutas, plazos, etiquetas de
sección, notas al pie). Ayuda a que la marca se lea como de ingeniería.

Los titulares llevan `text-wrap: balance` y `letter-spacing` negativo.

---

## 5. El cursor como sistema

Es lo que hace que el cursor sea marca y no un guiño de programador. **Significa que algo está a
punto de pasar**, que es exactamente lo que vende la agencia.

Aparece en cinco sitios:

1. **En el logo**, al final del wordmark.
2. **Como favicon y monograma**, convertido en caret.
3. **Como viñeta de las listas**, en lugar de un check genérico. Bloque siena de 8 × 13 px.
4. **Al final de los titulares de sección**, como el cursor que queda tras escribir la frase.
5. **Parpadeando en el botón mientras se envía un formulario**, en lugar de una ruedecita.
   Está enganchado a `:disabled`, así que funciona en los siete formularios sin JavaScript propio.

**Excepción:** no aparece en el articulado legal (`.legal-body`). Además de que ahí la decoración
sobra, empujaba titulares a dos líneas en móvil y dejaba el cursor solo en la segunda.

---

## 6. Tono de voz

Español de España, natural, sin jerga de agencia.

**Cómo se escribe:**

- **Frases cortas y concretas.** El cliente pidió literalmente «menos texto, fácil de digerir».
- **Habla de dolores reconocibles**, no de conceptos. «Alguien de tu equipo copia datos entre hojas»
  funciona; «optimización de procesos» no.
- **Primera persona del plural**, somos un equipo.
- **El verbo importa.** Se cambió «Obtener el curso» por «Acceder al curso» a petición suya.

**Qué no se escribe:**

- Nada de *revoluciona*, *potencia*, *transforma*, *desbloquea*, *soluciones integrales*.
- Nada de cifras sin fuente. Ver la regla dura en `PROYECTO.md`.
- Nada de presentar datos de terceros como propios.
- En inglés se escribe **AI**, nunca *artificial intelligence* desarrollado.

**Los agentes son una herramienta, no el producto.** Corrección explícita del cliente: la web vende
resolver problemas de empresa, y los agentes son uno de los medios.

---

## 7. Maquetación

- Contenedor de **1140 px**, con 24 px de margen lateral.
- Radios: **14 px** en tarjetas, **10 px** en botones.
- **Ningún texto puede saltar de línea antes de llenar su contenedor.** Requisito explícito del
  cliente. Nada de `max-width` estrechos en subtítulos ni titulares. Se verifica con un detector
  automático en escritorio y móvil antes de cada publicación.
- Punto de corte móvil habitual: **900 px**. Se prueba siempre a **390 px**.

---

## 8. Contacto visible

- **Email:** `info@algoryme.com`
- **WhatsApp Business:** +34 605 62 18 26, con botón flotante en toda la web
- **LinkedIn:** linkedin.com/in/rogelioalcaraz
- **CTA principal, siempre el mismo:** «Reserva una llamada de 30 minutos»

---

## 9. Ficheros

En `marca/`, con su propio `LEEME.md`:

| Fichero | Para qué |
|---|---|
| `algoryme-workspace-320x132.png` | Logo de organización en Google Workspace |
| `algoryme-horizontal-tinta.png` | Uso general sobre fondo claro |
| `algoryme-horizontal-blanco.png` | Sobre fondo oscuro o fotografía |
| `algoryme-horizontal-siena.png` | Cuando el logo va solo y debe destacar |
| `algoryme-perfil-horizontal.png` | Foto de perfil (se recorta en círculo) |
| `algoryme-perfil-horizontal-blanco.png` | Igual, más contraste |
| `algoryme-perfil-horizontal-siena.png` | Igual, fondo siena |
| `algoryme-perfil-caret-1024.png` | Solo el símbolo, para tamaños muy pequeños |

Todos con canal alfa salvo los de perfil, que van a sangre porque las plataformas los recortan.
