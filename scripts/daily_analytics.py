#!/usr/bin/env python3
"""
Email diario de analítica de Algoryme (GitHub Actions + OAuth, gratis).

El mismo token OAuth lee GA4 (API de datos) y envía el correo (API de Gmail): sin cuenta
de servicio ni contraseña SMTP. Corre desde .github/workflows/daily-analytics.yml a las
05:00 y 06:00 UTC; el guardia de abajo solo envía cuando en Madrid son las 7 (verano/invierno).

Contenido: KPIs de ayer + comparativa con la media de 7 días, gráfica de 90 días de visitantes
únicos, funnel de captación de los últimos 30 días (visitas → clic en agendar → leads → WhatsApp)
y desgloses de ayer (dispositivo, país, origen, páginas, eventos y proyecto).

Secrets: GA_CLIENT_ID, GA_CLIENT_SECRET, GA_REFRESH_TOKEN (opcionales GA4_PROPERTY_ID, MAIL_TO).
El recorrido visitante-por-visitante sería fase 2 (BigQuery o logger propio).
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
PROPERTY = os.environ.get("GA4_PROPERTY_ID") or "547553833"
MAIL_TO = os.environ.get("MAIL_TO") or "info@algoryme.com"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly",
          "https://www.googleapis.com/auth/gmail.send"]
SIENNA, INK, MUTED, LINE, GOOD = "#B5401C", "#211D18", "#6B6153", "#E4DFD4", "#31513F"
E = lambda s: H.escape(str(s), quote=False)

now = datetime.now(TZ)
if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" and now.hour != 7:
    print(f"En Madrid son las {now.hour}h, no toca enviar."); sys.exit(0)

yest = (now - timedelta(days=1)).date()
DAY = yest.isoformat()
DAY_ES = yest.strftime("%d/%m/%Y")
D30 = (yest - timedelta(days=29)).isoformat()
D90 = (yest - timedelta(days=89)).isoformat()

creds = Credentials(
    None, refresh_token=os.environ["GA_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["GA_CLIENT_ID"], client_secret=os.environ["GA_CLIENT_SECRET"],
    scopes=SCOPES)
client = BetaAnalyticsDataClient(credentials=creds)


def report(dims, mets, limit=10, order_metric=None, dim_filter=None,
           start=DAY, end=DAY, order_dim=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in mets],
        limit=limit)
    if order_metric:
        req.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True)]
    elif order_dim:
        req.order_bys = [OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name=order_dim))]
    if dim_filter:
        req.dimension_filter = dim_filter
    resp = client.run_report(req)
    return [[v.value for v in r.dimension_values] + [v.value for v in r.metric_values] for r in resp.rows]


def num(x):
    try: return int(round(float(x)))
    except Exception: return 0


def fmt_secs(s):
    s = num(s); m, sec = divmod(s, 60)
    return f"{m}m {sec:02d}s" if m else f"{sec}s"


# ---------- datos ----------
tot = report([], ["activeUsers", "sessions", "screenPageViews", "averageSessionDuration",
                  "newUsers", "engagementRate"], 1)
t = tot[0] if tot else ["0"] * 6

serie = report(["date"], ["activeUsers"], 400, order_dim="date", start=D90, end=DAY)
smap = {row[0]: num(row[1]) for row in serie}
dias = [(yest - timedelta(days=i)) for i in range(89, -1, -1)]
vals = [smap.get(d.strftime("%Y%m%d"), 0) for d in dias]
avg7 = sum(vals[-7:]) / 7 if len(vals) >= 7 else 0
sum30 = report([], ["activeUsers"], 1, start=D30, end=DAY)
uniq30 = num(sum30[0][0]) if sum30 else 0

ev30 = {r[0]: num(r[1]) for r in report(["eventName"], ["eventCount"], 60, "eventCount", start=D30, end=DAY)}

dispositivos = report(["deviceCategory"], ["activeUsers"], 10, "activeUsers")
paises = report(["country"], ["activeUsers"], 10, "activeUsers")
origenes = report(["sessionSourceMedium"], ["sessions"], 10, "sessions")
paginas = report(["pagePath"], ["screenPageViews"], 12, "screenPageViews")
eventos = report(["eventName"], ["eventCount"], 25, "eventCount")

proyectos = []
try:
    proyectos = report(["customEvent:proyecto"], ["eventCount"], 15, "eventCount",
        FilterExpression(filter=Filter(field_name="eventName",
            in_list_filter=Filter.InListFilter(values=["project_click", "project_expand"]))),
        start=D30, end=DAY)
    proyectos = [p for p in proyectos if p[0] and p[0] != "(not set)"]
except Exception:
    proyectos = []


# ---------- render ----------
def tabla(titulo, filas, cols):
    if not filas:
        return f'<h3 style="margin:24px 0 6px;font-size:15px">{E(titulo)}</h3><p style="color:{MUTED};margin:0">Sin datos.</p>'
    th = "".join(f'<th align="left" style="padding:4px 12px 4px 0;color:{MUTED};font-weight:600">{E(c)}</th>' for c in cols)
    tr = "".join("<tr>" + "".join(f'<td style="padding:3px 12px 3px 0">{E(v)}</td>' for v in f) + "</tr>" for f in filas)
    return (f'<h3 style="margin:24px 0 6px;font-size:15px">{E(titulo)}</h3>'
            f'<table style="border-collapse:collapse;font-size:14px"><tr>{th}</tr>{tr}</table>')


def kpi(n, l):
    return (f'<td style="padding:0 22px 0 0;vertical-align:top"><div style="font-size:26px;font-weight:800;color:{INK}">{E(n)}</div>'
            f'<div style="font-size:12px;color:{MUTED}">{E(l)}</div></td>')


def grafica(vals, dias):
    mx = max(vals) or 1
    pico = max(range(len(vals)), key=lambda i: vals[i])
    bars = ""
    for v in vals:
        h = max(2, round(96 * v / mx)) if v else 2
        col = SIENNA if v else LINE
        bars += (f'<td valign="bottom" style="padding:0 1px 0 0;height:96px">'
                 f'<div style="width:5px;height:{h}px;background:{col};border-radius:1px"></div></td>')
    ejes = (f'<div style="display:flex;justify-content:space-between;font-size:11px;color:{MUTED};margin-top:4px;max-width:540px">'
            f'<span>{dias[0].strftime("%d/%m")}</span><span>{dias[len(dias)//2].strftime("%d/%m")}</span><span>ayer</span></div>')
    return (f'<h3 style="margin:26px 0 8px;font-size:15px">Visitantes únicos · últimos 90 días</h3>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse"><tr>{bars}</tr></table>'
            f'{ejes}'
            f'<p style="font-size:12px;color:{MUTED};margin:6px 0 0">Pico: {vals[pico]} visitantes el {dias[pico].strftime("%d/%m")}.</p>')


# comparativa de ayer vs media de 7 días
ayer_u = num(t[0])
if avg7 > 0:
    d = (ayer_u - avg7) / avg7 * 100
    flecha = "▲" if d >= 0 else "▼"
    color = GOOD if d >= 0 else SIENNA
    comp = (f'<span style="color:{color};font-weight:700">{flecha} {abs(d):.0f}%</span> '
            f'<span style="color:{MUTED}">vs. media de 7 días ({avg7:.1f}/día)</span>')
else:
    comp = f'<span style="color:{MUTED}">Sin media de 7 días todavía.</span>'


def funnel_row(label, n, pct=None):
    right = f'<span style="color:{MUTED};font-size:12px"> · {pct}</span>' if pct else ''
    return (f'<tr><td style="padding:5px 0;border-bottom:1px solid {LINE};font-size:14px">{E(label)}</td>'
            f'<td align="right" style="padding:5px 0;border-bottom:1px solid {LINE};font-size:15px;font-weight:700">{E(n)}{right}</td></tr>')


clic = ev30.get("book_call_click", 0)
leads = ev30.get("generate_lead", 0)
wa = ev30.get("whatsapp_click", 0)
nl = ev30.get("newsletter_signup", 0)
def pc(x): return f'{100*x/uniq30:.1f}%' if uniq30 else '-'
funnel = (f'<h3 style="margin:26px 0 6px;font-size:15px">Captación · últimos 30 días</h3>'
          f'<table style="border-collapse:collapse;width:100%;max-width:420px">'
          f'{funnel_row("Visitantes únicos", uniq30)}'
          f'{funnel_row("Clic en «Agendar llamada»", clic, pc(clic))}'
          f'{funnel_row("Formularios de lead enviados", leads, pc(leads))}'
          f'{funnel_row("Clics a WhatsApp", wa)}'
          f'{funnel_row("Altas en newsletter", nl)}'
          f'</table>')

body = f'''<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:{INK};max-width:680px">
  <p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:{SIENNA};font-weight:700;margin:0">Algoryme · analítica</p>
  <h2 style="margin:2px 0 8px">Ayer, {E(DAY_ES)}</h2>
  <table role="presentation" cellpadding="0" cellspacing="0"><tr>
    {kpi(t[0],"visitantes")}{kpi(t[1],"sesiones")}{kpi(t[2],"páginas vistas")}
    {kpi(fmt_secs(t[3]),"tiempo medio")}{kpi(num(t[4]),"nuevos")}{kpi(f"{num(float(t[5])*100)}%","engagement")}
  </tr></table>
  <p style="margin:10px 0 0;font-size:14px">{comp}</p>
  {grafica(vals, dias)}
  {funnel}
  {tabla("Dispositivo (ayer)", dispositivos, ["Tipo","Visitantes"])}
  {tabla("País (ayer)", paises, ["País","Visitantes"])}
  {tabla("De dónde vienen (ayer)", origenes, ["Origen / medio","Sesiones"])}
  {tabla("Páginas más vistas (ayer)", paginas, ["Ruta","Vistas"])}
  {tabla("Eventos (ayer)", eventos, ["Evento","Veces"])}
  {tabla("Qué proyecto han mirado (30 días)", proyectos, ["Proyecto","Veces"]) if proyectos else ""}
  <p style="font-size:12px;color:{MUTED};margin-top:28px;border-top:1px solid {LINE};padding-top:12px">
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
