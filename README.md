# Algoryme

Web de **Algoryme**, consultoría de inteligencia artificial para empresas.

Sitio estático, sin build: cada página es un `.html` autocontenido con su CSS en línea
y el diccionario de textos embebido. La única petición externa son las fuentes de Google.

- **Textos**: `content.json` es la fuente de la verdad (ES/EN). Al editarlo hay que
  re-embeber el diccionario minificado en las 14 páginas y re-hornear el texto estático español.
- **Formularios**: se envían por AJAX a FormSubmit. El buzón real es privado; el email
  visible en la web es `info@algoryme.com`.
- **Despliegue**: GitHub Pages desde `main`.

## Regla dura del proyecto

Ningún dato, cliente, logo o métrica de esta web puede ser inventado. Si un dato no está
verificado, se omite o se formula de manera cualitativa. Las cifras de terceros van con su fuente.
