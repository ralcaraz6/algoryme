# Algoryme

Web de **Algoryme**, consultoría de inteligencia artificial para empresas.
En producción: **https://algoryme.com**

## Empieza por aquí

| Documento | Qué contiene |
|---|---|
| **[PROYECTO.md](PROYECTO.md)** | Qué es, cómo está construido, las trampas conocidas y lo que queda pendiente. **Léelo antes de tocar nada.** |
| **[MARCA.md](MARCA.md)** | Guía de marca: logo, color, tipografía, tono de voz y el sistema del cursor. |
| [marca/LEEME.md](marca/LEEME.md) | Qué fichero de logo usar en cada sitio. |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Contexto de **Rachea** y **Prospéctalo**, los dos productos de suscripción. Su código vive en otros repositorios; aquí solo se enlazan. |

## En dos líneas

Sitio estático sin compilación: 18 páginas HTML autocontenidas, con el CSS y el diccionario de
textos embebidos en cada una. `content.json` es la fuente de la verdad de los textos (ES/EN), pero
va embebido minificado en cada página, así que **al editar textos hay que re-embeber y re-hornear**.

Se despliega con un *push* a `main`.

## Regla dura

> Ningún dato, cliente, logo o métrica de esta web puede ser inventado. Si un dato no está
> verificado, se omite o se formula de manera cualitativa. Las cifras de terceros van con su fuente.
