#!/usr/bin/env python3
"""
Email diario de analítica de Algoryme.

Lee los datos de AYER desde la API de datos de GA4 (gratuita, sin BigQuery) y envía
un correo a info@algoryme.com por SMTP. Estructura: primero datos agregados, luego
los desgloses (dispositivo, país, origen, páginas, eventos y, si está registrada la
dimensión personalizada 'proyecto', qué proyecto han clicado).

El recorrido visitante-por-visitante NO está aquí: la API de GA4 no expone usuarios
individuales. Eso necesitaría BigQuery o un logger propio (fase 2).

Variables de entorno (se pasan como secrets de GitHub Actions):
  GA4_SA_JSON       -> contenido JSON de la cuenta de servicio con acceso Lector a la propiedad
  GA4_PROPERTY_ID   -> id numérico de la propiedad (por defecto 547553833)
  SMTP_HOST         -> por defecto smtp.gmail.com
  SMTP_PORT         -> por defecto 587
  SMTP_USER         -> info@algoryme.com
  SMTP_PASSWORD     -> contraseña de aplicación de Google
  MAIL_TO           -> por defecto info@algoryme.com
"""
import os, json, smtplib, html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from email.mime.text import MIMEText
from email.utils import formataddr

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, OrderBy,
)

PROPERTY = os.environ.get("GA4_PROPERTY_ID", "547553833")
MAIL_TO = os.environ.get("MAIL_TO", "info@algoryme.com")
TZ = ZoneInfo("Europe/Madrid")
E = lambda s: html.escape(str(s), quote=False)

# --- ayer en hora de Madrid ---
yesterday = (datetime.now(TZ) - timedelta(days=1)).date()
DAY = yesterday.isoformat()
DAY_ES = yesterday.strftime("%d/%m/%Y")

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GA4_SA_JSON"]),
    scopes=["https://www.googleapis.com/auth/analytics.readonly"],
)
client = BetaAnalyticsDataClient(credentials=creds)


def report(dimensions, metrics, limit=10, order_metric=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY}",
        date_ranges=[DateRange(start_date=DAY, end_date=DAY)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
    )
    if order_metric:
        req.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True)]
    return client.run_report(req)


def rows(resp):
    out = []
    for r in resp.rows:
        out.append([v.value for v in r.dimension_values] + [v.value for v in r.metric_values])
    return out


def fmt_secs(s):
    try:
        s = float(s)
    except Exception:
        return "-"
    m, sec = divmod(int(round(s)), 60)
    return f"{m}m {sec:02d}s" if m else f"{sec}s"


# ---------- 1. TOTALES ----------
tot = rows(report([], ["activeUsers", "sessions", "screenPageViews", "averageSessionDuration"], limit=1))
if tot:
    usuarios, sesiones, vistas, dur = tot[0]
else:
    usuarios = sesiones = vistas = "0"; dur = "0"

# ---------- desgloses ----------
dispositivos = rows(report(["deviceCategory"], ["activeUsers"], 10, "activeUsers"))
paises = rows(report(["country"], ["activeUsers"], 10, "activeUsers"))
origenes = rows(report(["sessionSourceMedium"], ["sessions"], 10, "sessions"))
paginas = rows(report(["pagePath"], ["screenPageViews"], 12, "screenPageViews"))
eventos = rows(report(["eventName"], ["eventCount"], 25, "eventCount"))

# qué proyecto han clicado (solo si la dimensión personalizada 'proyecto' está registrada)
proyectos = []
try:
    from google.analytics.data_v1beta.types import Filter, FilterExpression
    req = RunReportRequest(
        property=f"properties/{PROPERTY}",
        date_ranges=[DateRange(start_date=DAY, end_date=DAY)],
        dimensions=[Dimension(name="customEvent:proyecto")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(filter=Filter(
            field_name="eventName",
            in_list_filter=Filter.InListFilter(values=["project_click", "project_expand"]))),
        limit=15,
    )
    proyectos = rows(client.run_report(req))
    proyectos = [p for p in proyectos if p[0] and p[0] != "(not set)"]
except Exception:
    proyectos = []


# ---------- email HTML ----------
def tabla(titulo, filas, cols):
    if not filas:
        return f'<h3 style="margin:22px 0 6px;font-size:15px">{E(titulo)}</h3><p style="color:#6B6153;margin:0">Sin datos.</p>'
    th = "".join(f'<th align="left" style="padding:4px 10px 4px 0;color:#6B6153;font-weight:600">{E(c)}</th>' for c in cols)
    trs = ""
    for f in filas:
        tds = "".join(f'<td style="padding:3px 10px 3px 0">{E(v)}</td>' for v in f)
        trs += f"<tr>{tds}</tr>"
    return (f'<h3 style="margin:22px 0 6px;font-size:15px">{E(titulo)}</h3>'
            f'<table style="border-collapse:collapse;font-size:14px"><tr>{th}</tr>{trs}</table>')

kpi = f'''<div style="display:flex;gap:24px;flex-wrap:wrap;margin:6px 0 4px">
  <div><div style="font-size:26px;font-weight:800;color:#211D18">{E(usuarios)}</div><div style="font-size:12px;color:#6B6153">visitantes</div></div>
  <div><div style="font-size:26px;font-weight:800;color:#211D18">{E(sesiones)}</div><div style="font-size:12px;color:#6B6153">sesiones</div></div>
  <div><div style="font-size:26px;font-weight:800;color:#211D18">{E(vistas)}</div><div style="font-size:12px;color:#6B6153">páginas vistas</div></div>
  <div><div style="font-size:26px;font-weight:800;color:#211D18">{E(fmt_secs(dur))}</div><div style="font-size:12px;color:#6B6153">tiempo medio/sesión</div></div>
</div>'''

body = f'''<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#211D18;max-width:680px">
  <p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#B5401C;font-weight:700;margin:0">Algoryme · analítica</p>
  <h2 style="margin:2px 0 2px">Ayer, {E(DAY_ES)}</h2>
  {kpi}
  {tabla("Dispositivo", dispositivos, ["Tipo", "Visitantes"])}
  {tabla("País", paises, ["País", "Visitantes"])}
  {tabla("De dónde vienen", origenes, ["Origen / medio", "Sesiones"])}
  {tabla("Páginas más vistas", paginas, ["Ruta", "Vistas"])}
  {tabla("Qué han hecho (eventos)", eventos, ["Evento", "Veces"])}
  {tabla("Qué proyecto han mirado", proyectos, ["Proyecto", "Veces"]) if proyectos else ""}
  <p style="font-size:12px;color:#6B6153;margin-top:26px;border-top:1px solid #E4DFD4;padding-top:12px">
    Solo cuentan visitas que aceptaron cookies. El recorrido visitante por visitante no está en la API de GA4
    (necesita BigQuery o un logger propio). Las cifras de ayer pueden ajustarse ligeramente durante el día.</p>
</div>'''

msg = MIMEText(body, "html", "utf-8")
msg["Subject"] = f"Algoryme · analítica de ayer ({DAY_ES})"
msg["From"] = formataddr(("Algoryme Analytics", os.environ.get("SMTP_USER", MAIL_TO)))
msg["To"] = MAIL_TO

host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
port = int(os.environ.get("SMTP_PORT", "587"))
with smtplib.SMTP(host, port) as s:
    s.starttls()
    s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
    s.send_message(msg)
print(f"Email enviado a {MAIL_TO} con los datos de {DAY}")
