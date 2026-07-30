#!/usr/bin/env python3
"""
Email diario de analítica de Algoryme (GitHub Actions + OAuth, gratis).

Lee los datos de AYER desde la API de datos de GA4 y envía un correo a MAIL_TO por la
API de Gmail. El MISMO token OAuth sirve para leer GA4 y para enviar el correo, así que
no hace falta ni cuenta de servicio ni contraseña SMTP.

Se ejecuta desde .github/workflows/daily-analytics.yml a las 05:00 y 06:00 UTC; el guardia
de abajo solo envía cuando en Madrid son las 7, así que es siempre las 7am (verano/invierno).

Secrets (en el repo de GitHub):
  GA_CLIENT_ID, GA_CLIENT_SECRET, GA_REFRESH_TOKEN  -> token OAuth (ver scripts/get_token.py)
  GA4_PROPERTY_ID  (opcional, por defecto 547553833)
  MAIL_TO          (opcional, por defecto info@algoryme.com)

El recorrido visitante-por-visitante NO está aquí: la API de GA4 no expone usuarios
individuales. Eso sería fase 2 (BigQuery o logger propio).
"""
import os, sys, base64, html as H
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, OrderBy, Filter, FilterExpression,
)
from googleapiclient.discovery import build

TZ = ZoneInfo("Europe/Madrid")
PROPERTY = os.environ.get("GA4_PROPERTY_ID", "547553833")
MAIL_TO = os.environ.get("MAIL_TO", "info@algoryme.com")
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly",
          "https://www.googleapis.com/auth/gmail.send"]
E = lambda s: H.escape(str(s), quote=False)

# --- solo enviar a las 7 de Madrid (o si es ejecución manual desde Actions) ---
now = datetime.now(TZ)
if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" and now.hour != 7:
    print(f"En Madrid son las {now.hour}h, no toca enviar."); sys.exit(0)

yesterday = (now - timedelta(days=1)).date()
DAY = yesterday.isoformat()
DAY_ES = yesterday.strftime("%d/%m/%Y")

creds = Credentials(
    None,
    refresh_token=os.environ["GA_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["GA_CLIENT_ID"],
    client_secret=os.environ["GA_CLIENT_SECRET"],
    scopes=SCOPES,
)
client = BetaAnalyticsDataClient(credentials=creds)


def report(dims, mets, limit=10, order_metric=None, dim_filter=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY}",
        date_ranges=[DateRange(start_date=DAY, end_date=DAY)],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in mets],
        limit=limit,
    )
    if order_metric:
        req.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True)]
    if dim_filter:
        req.dimension_filter = dim_filter
    resp = client.run_report(req)
    return [[v.value for v in r.dimension_values] + [v.value for v in r.metric_values] for r in resp.rows]


def fmt_secs(s):
    try:
        s = int(round(float(s)))
    except Exception:
        return "-"
    m, sec = divmod(s, 60)
    return f"{m}m {sec:02d}s" if m else f"{sec}s"


# ---------- datos ----------
tot = report([], ["activeUsers", "sessions", "screenPageViews", "averageSessionDuration"], 1)
t = tot[0] if tot else ["0", "0", "0", "0"]
dispositivos = report(["deviceCategory"], ["activeUsers"], 10, "activeUsers")
paises = report(["country"], ["activeUsers"], 10, "activeUsers")
origenes = report(["sessionSourceMedium"], ["sessions"], 10, "sessions")
paginas = report(["pagePath"], ["screenPageViews"], 12, "screenPageViews")
eventos = report(["eventName"], ["eventCount"], 25, "eventCount")

proyectos = []
try:
    proyectos = report(
        ["customEvent:proyecto"], ["eventCount"], 15, "eventCount",
        FilterExpression(filter=Filter(field_name="eventName",
            in_list_filter=Filter.InListFilter(values=["project_click", "project_expand"]))))
    proyectos = [p for p in proyectos if p[0] and p[0] != "(not set)"]
except Exception:
    proyectos = []


# ---------- email ----------
def tabla(titulo, filas, cols):
    if not filas:
        return f'<h3 style="margin:22px 0 6px;font-size:15px">{E(titulo)}</h3><p style="color:#6B6153;margin:0">Sin datos.</p>'
    th = "".join(f'<th align="left" style="padding:4px 12px 4px 0;color:#6B6153;font-weight:600">{E(c)}</th>' for c in cols)
    tr = "".join("<tr>" + "".join(f'<td style="padding:3px 12px 3px 0">{E(v)}</td>' for v in f) + "</tr>" for f in filas)
    return (f'<h3 style="margin:22px 0 6px;font-size:15px">{E(titulo)}</h3>'
            f'<table style="border-collapse:collapse;font-size:14px"><tr>{th}</tr>{tr}</table>')


def kpi(n, l):
    return (f'<div style="margin-right:24px"><div style="font-size:26px;font-weight:800;color:#211D18">{E(n)}</div>'
            f'<div style="font-size:12px;color:#6B6153">{E(l)}</div></div>')


body = f'''<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#211D18;max-width:680px">
  <p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#B5401C;font-weight:700;margin:0">Algoryme · analítica</p>
  <h2 style="margin:2px 0 8px">Ayer, {E(DAY_ES)}</h2>
  <div style="display:flex;flex-wrap:wrap">{kpi(t[0],"visitantes")}{kpi(t[1],"sesiones")}{kpi(t[2],"páginas vistas")}{kpi(fmt_secs(t[3]),"tiempo medio/sesión")}</div>
  {tabla("Dispositivo", dispositivos, ["Tipo","Visitantes"])}
  {tabla("País", paises, ["País","Visitantes"])}
  {tabla("De dónde vienen", origenes, ["Origen / medio","Sesiones"])}
  {tabla("Páginas más vistas", paginas, ["Ruta","Vistas"])}
  {tabla("Qué han hecho (eventos)", eventos, ["Evento","Veces"])}
  {tabla("Qué proyecto han mirado", proyectos, ["Proyecto","Veces"]) if proyectos else ""}
  <p style="font-size:12px;color:#6B6153;margin-top:26px;border-top:1px solid #E4DFD4;padding-top:12px">
    Solo cuentan visitas que aceptaron cookies. El recorrido visitante por visitante no está en la API de GA4
    (necesita BigQuery o un logger propio). Las cifras de ayer pueden ajustarse ligeramente durante el día.</p>
</div>'''

msg = MIMEText(body, "html", "utf-8")
msg["To"] = MAIL_TO
msg["From"] = MAIL_TO
msg["Subject"] = f"Algoryme · analítica de ayer ({DAY_ES})"
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)
gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
print(f"Email enviado a {MAIL_TO} con los datos de {DAY}")
