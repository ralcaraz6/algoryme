# Rachea y Prospéctalo — guía de los productos

Documento de contexto para retomar el trabajo en las dos herramientas de suscripción de Algoryme.
Si eres una IA que empieza una sesión nueva sobre uno de los dos productos, **lee esto antes de
tocar nada**.

> **Este repositorio no contiene el código de las herramientas.** Aquí vive la web de la agencia, que
> solo las enlaza desde `herramientas.html`. El código de cada producto está en su propio
> repositorio; este documento existe para que el contexto no se pierda entre sesiones.

Estado a **22 de julio de 2026**.

---

## 1. Qué son

Dos micro-SaaS de suscripción, hermanos, publicados por Algoryme.

| | Rachea | Prospéctalo |
|---|---|---|
| **Qué es** | Gestor de tareas **+ seguidor de hábitos** | Pipeline de ventas para autónomos |
| **Dominio** | https://rachea.com | https://prospectalo.com |
| **Repositorio (privado)** | `github.com/ralcaraz6/rachea` | `github.com/ralcaraz6/prospectalo` |
| **Carpeta local** | `/Users/rogelio/tt/pulpo-action` | `/Users/rogelio/tt/prospecta-pulpo` |
| **Precio** | 4,99 €/mes · 79 €/año | 4,99 €/mes · 79 €/año |

**Los repositorios se renombraron el 27-jul-2026** de `pulpo-action-3` y `prospecta-pulpo` a `rachea`
y `prospectalo`. Dos cosas que conviene saber:

- **Las carpetas locales siguen con el nombre viejo** (`pulpo-action`, `prospecta-pulpo`). Renombrar
  el repositorio en GitHub no toca el directorio de tu máquina. Si las alineas, es un `mv` aparte.
- **GitHub deja redirecciones** desde los nombres antiguos, así que un `clone` o un `push` con la URL
  vieja sigue funcionando. Aun así, actualiza los remotos para no depender de ellas:
  `git remote set-url origin https://github.com/ralcaraz6/rachea`. Y **no recrees los nombres
  viejos**: si algún día existe otro repo llamado `pulpo-action-3`, la redirección se rompe.

El nombre de Prospéctalo va **sin tilde** (`prospectalo`) porque GitHub solo admite ASCII en los
nombres de repositorio; con tilde habría quedado `Prosp-ctalo`.

La agencia matriz vive aparte, en este repositorio: `github.com/ralcaraz6/algoryme`, publicado en
GitHub Pages. Su página `herramientas.html` enlaza a las dos.

## 2. El embudo (idéntico en las dos)

```
Landing (/)  →  Crear cuenta (/crear-cuenta)  →  Precios (/precios)
   →  Stripe Checkout  →  Bienvenida (/bienvenida)  →  App (/app)
```

- Registro con **email + contraseña** o **Google Sign-In**.
- En el registro hay **dos casillas obligatorias**: aceptar condiciones y privacidad, y solicitar el
  inicio inmediato del servicio. Lo segundo permite prorratear la devolución si alguien desiste en
  los 14 días tras haber usado el producto.
- `/app` solo es accesible con **suscripción activa**; si no, redirige a `/precios`.
- El estado de la suscripción lo marca el **webhook de Stripe** (fuente de la verdad). Al volver de
  Checkout también se comprueba la sesión directamente, por si el webhook aún no ha llegado.

## 3. Cómo están construidos

**Cloudflare Workers + D1 (SQLite gestionado) + Hono.** Sin compilación, sin servidor que mantener,
dentro del plan gratuito de Cloudflare. Frontend en HTML, CSS y JavaScript vanilla: cero framework,
cero *bundler*.

```
wrangler.toml            configuración de Cloudflare (D1, assets, rutas, dominio)
schema.sql               esquema de la base de datos
worker/index.js          rutas y arranque (Hono)
worker/auth.js           sesión JWT en cookie, contraseñas PBKDF2, altas
worker/rutas-auth.js     registro, login, Google OAuth
worker/rutas-billing.js  Stripe Checkout, portal de cliente y webhook
worker/rutas-tareas.js   (Rachea) API del tablero
worker/rutas-habitos.js  (Rachea) API de hábitos
worker/rutas-pipeline.js (Prospéctalo) API del pipeline
vistas/app.html          HTML de la app — FUERA de public/ a propósito (ver §5)
public/                  landing, registro, precios, legales, css, js, i18n
public/araki.css         sistema de diseño compartido
```

### Arrancar en local

```bash
cd pulpo-action        # o prospecta-pulpo (las carpetas conservan el nombre viejo)
npm install
npm run db:local       # crea la base de datos local
npm run dev            # Rachea en :5090, Prospéctalo en :5091
```

Secretos de desarrollo en `.dev.vars` (ignorado por git). En producción se cargan con
`wrangler secret put NOMBRE`. Los nombres: `JWT_SECRET`, `STRIPE_SECRET_KEY`,
`STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_MENSUAL`, `STRIPE_PRICE_ANUAL`, `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`.

**Las claves nunca se pegan en un chat.** Se cargan siempre con `wrangler secret put`.

### Desplegar

```bash
npm run deploy         # wrangler deploy
```

## 4. Modelo de datos

**Común:** `users` (email, name, password_hash, google_id, stripe_customer_id,
stripe_subscription_id, plan, status).

**Rachea:** `arms` (áreas de vida, máx. 8) · `tasks` (estado entrada/hoy/curso/hecho, prioridad,
fecha, foco) · `habits` (objetivo semanal 1-7) · `habit_logs` (una marca por hábito y día, con
índice único).

**Prospéctalo:** `deals` (oportunidades; el campo que manda es `next_step`) · `touches` (historial de
contactos por oportunidad).

## 5. Decisiones y trampas conocidas (el porqué)

Estas son las decisiones no obvias. Si vas a tocar algo, entiende primero por qué está como está.

### Producto

- **Rachea no mezcla tareas y hábitos en el mismo tablero.** Una tarea se cierra una vez; un hábito
  se sostiene. Son dos cosas distintas, así que viven en dos vistas (pestañas `Tablero` / `Hábitos`,
  tecla `H` para saltar). Meterlas juntas estropearía las dos.
- **La tarjeta de Prospéctalo enseña el PRÓXIMO PASO, no el contacto.** «Reenviar el caso de la
  clínica», y debajo en gris «Marta · Dentalia». Lo primero mueve, lo segundo solo identifica. De ahí
  sale la métrica que hace útil la herramienta: cuántas oportunidades tienes **sin próximo paso**
  (sale en ámbar).
- **Los límites son a propósito:** 8 brazos en Rachea, 12 hábitos. El límite es la función: si todo
  cabe, nada prioriza.
- **Captura en lenguaje natural** (Rachea): `Llamar a David mañana !alta #ventas` se parte en título,
  fecha, prioridad y brazo. Entiende ES y EN.

### Ingeniería

- **PBKDF2-SHA256 para contraseñas, no bcrypt.** WebCrypto es nativo en Workers; bcrypt en JS puro se
  comería el presupuesto de CPU de cada petición.
- **`hono/jwt` exige declarar el algoritmo (`HS256`) al firmar Y al verificar.** Sin eso la sesión
  falla en silencio.
- **`vistas/app.html` vive fuera de `public/`** y se incrusta en el *bundle*. Si estuviera en los
  estáticos, Cloudflare lo serviría en `/app` saltándose la comprobación de sesión y de suscripción.
  Es un agujero real que ya se cerró una vez; no muevas ese fichero.
- **Fechas en hora local del navegador, no del servidor.** `date('now')` en UTC haría que marcar un
  hábito a las 23:30 en España cayera en el día siguiente.
- **Importes en céntimos** (Prospéctalo), nunca decimales flotantes.
- **`api()` no asume que la respuesta es JSON.** Durante la propagación de un despliegue, una ruta
  nueva puede devolver el 404 de los estáticos (HTML); antes eso rompía la vista entera. Ahora
  devuelve `null` y quien llama decide.
- **El webhook exige firma en producción.** Sin `STRIPE_WEBHOOK_SECRET` y con `NODE_ENV=production`,
  devuelve 503 en vez de aceptar el evento. Sin esto, cualquiera podría activarse una suscripción con
  un POST.
- **`routes` (dominio propio) va ANTES de cualquier `[tabla]` en `wrangler.toml`.** En TOML, después
  de una tabla se lee como clave de esa tabla, y wrangler lo ignora en silencio: ni despliega el
  dominio ni avisa.

### Diseño

Sistema **Araki** (ver `GUIA-DE-MARCA.md` en cada repositorio de producto): tinta sobre papel, el
color solo cuando significa algo. Es el mismo en las dos herramientas, y **deliberadamente distinto
del diseño cálido de Algoryme** (ver `MARCA.md`) para no confundir agencia y producto.

## 6. Notas de marca

Leer antes de tocar textos públicos.

- **La agencia se llama ahora Algoryme**, no Action Labs. Pero el pie de las dos apps aún dice *«una
  herramienta de Action Labs»* (`public/i18n.js`, claves `ui.footer` y `ui.footerTerms`). **Decisión
  pendiente del dueño**: actualizar a Algoryme o dejarlo. No se cambió por cuenta propia porque es
  texto de marca.
- El nombre **Rachea** viene de «racha», el corazón del producto: hábitos y rachas. Logo: tres
  cuadros de días, el último a media opacidad (el de hoy, pendiente).
- **Prospéctalo** es un verbo en imperativo, a propósito: dice lo que haces, no lo que es. Logo: tres
  barras ascendentes.
- Ambos logos son SVG en línea, embebidos en cada HTML y como `favicon` en data-URI.

## 7. Estado actual

### Funcionando y verificado en producción

- Las dos apps en sus dominios con HTTPS (`rachea.com`, `prospectalo.com`, y sus `www`).
- Registro, login y Google Sign-In, redirigiendo a los dominios propios.
- Stripe Checkout y **webhooks firmados que activan la cuenta** (probado con un evento firmado real,
  no simulado).
- Páginas legales (condiciones y privacidad), bilingües, enlazadas desde el pie y desde el registro.
- Todo bilingüe ES/EN, idioma recordado en `localStorage` y forzable con `?lang=en`.
- Stripe: nombres de cuenta, productos, iconos y colores actualizados.

### Pendiente — requiere acciones del dueño, no de código

1. **Probar un pago con tarjeta de punta a punta.** Nadie lo ha hecho aún como cliente. Tarjeta de
   test: `4242 4242 4242 4242`, fecha futura, CVC cualquiera.
2. **Rellenar los datos del titular en las legales.** Las páginas `/condiciones` y `/privacidad`
   llevan `[NOMBRE]`, `[NIF]`, `[DIRECCIÓN]` y `[EMAIL]` con un aviso ámbar. Sin esto no cumplen la
   LSSI y no se puede cobrar en regla.
3. **Activar las cuentas de Stripe** (nombre público del negocio → «Rachea» / «Prospéctalo»). Ahora
   el checkout de Rachea muestra «Pulpo347» en la cabecera; se corrige al activar la cuenta, que hace
   falta igualmente para cobrar de verdad. Prospéctalo ya sale bien.
4. **Pasar Stripe a modo LIVE** cuando se vaya a cobrar de verdad: repetir producto, precios, claves
   y webhooks en live.
5. **Borrar la credencial OAuth vieja de Google** («Pulpo Action 3», del 19 de julio).

### Mejoras técnicas anotadas — no bloquean

- Recuperación de contraseña por email.
- Verificación de email en el registro.
- Alojar Google Fonts en propio. Ahora se cargan de Google, que recibe la IP del visitante; está
  declarado en la política de privacidad, pero mejor evitarlo.
- Prueba gratuita de X días antes del cobro.
