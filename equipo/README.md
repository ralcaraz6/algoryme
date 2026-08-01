# Fotos del equipo

Guarda aquí una foto por persona con **exactamente** este nombre:

| Fichero | Persona | Rol |
|---|---|---|
| `rogelio-alcaraz.jpg` | Rogelio Alcaraz | Director |
| `andrew-schwartz.jpg` | Andrew Schwartz | Project Manager |
| `luis-paloma.jpg` | Luis Paloma | AI Specialist |
| `massimo-angelini.jpg` | Massimo Angelini | AI Specialist |
| `paula-camprecios.jpg` | Paula Campreciós | AI Specialist |
| `alvaro-entrena.jpg` | Álvaro Entrena | Trainee |

No hace falta que las recortes: sirve cualquier foto (JPG o PNG, mejor si es de 400 px para arriba).

Guarda el original en `_src/` con ese nombre. Desde ago-2026 la foto buena la genera **`uniformar.py`**, que recorta el fondo original, compone a todo el mundo sobre el mismo fondo de marca, encuadra todas las cabezas al mismo tamaño y aplica el mismo tratamiento de color. Es lo que hace que los seis retratos parezcan un mismo set:

```bash
python3 -m venv .venv && .venv/bin/pip install rembg onnxruntime pillow
.venv/bin/python equipo/uniformar.py
```

La primera ejecución se descarga un modelo de 176 MB. La salida es `equipo/<slug>.jpg` a 640×640.

`procesar.py` es el script anterior: solo recorta a la cara y actualiza las tarjetas del equipo en todas las páginas, sin tocar el fondo. Quien no tenga foto se queda con su monograma de iniciales.
