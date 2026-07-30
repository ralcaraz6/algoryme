/**
 * Email diario de analítica de Algoryme — Google Apps Script.
 *
 * Corre en la cuenta de Google de Algoryme (independiente de SVI). Cada mañana lee
 * los datos de AYER de GA4 (API de datos, gratis, sin BigQuery ni claves) y se envía
 * un correo a MAIL_TO. El disparador va en hora de Madrid, así que es siempre ~7am
 * todo el año (verano e invierno).
 *
 * Puesta en marcha (ver los pasos que te pasé): pega esto en un proyecto de
 * script.google.com, activa el servicio avanzado "Google Analytics Data API",
 * pon un disparador diario 7-8am y autorízalo una vez.
 */
const PROPERTY_ID = '547553833';        // tu propiedad GA4 (sale de la URL de GA4). Confírmalo.
const MAIL_TO     = 'info@algoryme.com';
const TZ          = 'Europe/Madrid';

function emailDiarioAnalitica() {
  const ayer = new Date();
  ayer.setDate(ayer.getDate() - 1);
  const dia   = Utilities.formatDate(ayer, TZ, 'yyyy-MM-dd');
  const diaEs = Utilities.formatDate(ayer, TZ, 'dd/MM/yyyy');

  function report(dims, mets, limit, orderMetric, dimFilter) {
    const req = {
      dateRanges: [{ startDate: dia, endDate: dia }],
      dimensions: (dims || []).map(function (n) { return { name: n }; }),
      metrics:    (mets || []).map(function (n) { return { name: n }; }),
      limit: limit || 10
    };
    if (orderMetric) req.orderBys = [{ metric: { metricName: orderMetric }, desc: true }];
    if (dimFilter)   req.dimensionFilter = dimFilter;
    const resp = AnalyticsData.Properties.runReport(req, 'properties/' + PROPERTY_ID);
    return (resp.rows || []).map(function (r) {
      return (r.dimensionValues || []).map(function (v) { return v.value; })
        .concat((r.metricValues || []).map(function (v) { return v.value; }));
    });
  }

  // ---- 1. totales ----
  const tot = report([], ['activeUsers', 'sessions', 'screenPageViews', 'averageSessionDuration'], 1);
  const t = tot[0] || ['0', '0', '0', '0'];

  // ---- desgloses ----
  const dispositivos = report(['deviceCategory'], ['activeUsers'], 10, 'activeUsers');
  const paises       = report(['country'], ['activeUsers'], 10, 'activeUsers');
  const origenes     = report(['sessionSourceMedium'], ['sessions'], 10, 'sessions');
  const paginas      = report(['pagePath'], ['screenPageViews'], 12, 'screenPageViews');
  const eventos      = report(['eventName'], ['eventCount'], 25, 'eventCount');

  // qué proyecto han mirado (solo si registras la dimensión personalizada 'proyecto')
  let proyectos = [];
  try {
    proyectos = report(['customEvent:proyecto'], ['eventCount'], 15, 'eventCount', {
      filter: { fieldName: 'eventName', inListFilter: { values: ['project_click', 'project_expand'] } }
    }).filter(function (p) { return p[0] && p[0] !== '(not set)'; });
  } catch (e) { proyectos = []; }

  // ---- email ----
  function esc(s) { return String(s).replace(/[<>&]/g, function (c) { return { '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]; }); }
  function secs(s) { s = Math.round(Number(s) || 0); const m = Math.floor(s / 60), r = s % 60; return m ? (m + 'm ' + (r < 10 ? '0' : '') + r + 's') : (r + 's'); }
  function tabla(titulo, filas, cols) {
    if (!filas.length) return '<h3 style="margin:22px 0 6px;font-size:15px">' + esc(titulo) + '</h3><p style="color:#6B6153;margin:0">Sin datos.</p>';
    const th = cols.map(function (c) { return '<th align="left" style="padding:4px 12px 4px 0;color:#6B6153;font-weight:600">' + esc(c) + '</th>'; }).join('');
    const tr = filas.map(function (f) { return '<tr>' + f.map(function (v) { return '<td style="padding:3px 12px 3px 0">' + esc(v) + '</td>'; }).join('') + '</tr>'; }).join('');
    return '<h3 style="margin:22px 0 6px;font-size:15px">' + esc(titulo) + '</h3><table style="border-collapse:collapse;font-size:14px"><tr>' + th + '</tr>' + tr + '</table>';
  }
  function kpi(n, l) { return '<div style="margin-right:24px"><div style="font-size:26px;font-weight:800;color:#211D18">' + esc(n) + '</div><div style="font-size:12px;color:#6B6153">' + esc(l) + '</div></div>'; }

  const html =
    '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#211D18;max-width:680px">' +
      '<p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#B5401C;font-weight:700;margin:0">Algoryme · analítica</p>' +
      '<h2 style="margin:2px 0 8px">Ayer, ' + esc(diaEs) + '</h2>' +
      '<div style="display:flex;flex-wrap:wrap">' + kpi(t[0], 'visitantes') + kpi(t[1], 'sesiones') + kpi(t[2], 'páginas vistas') + kpi(secs(t[3]), 'tiempo medio/sesión') + '</div>' +
      tabla('Dispositivo', dispositivos, ['Tipo', 'Visitantes']) +
      tabla('País', paises, ['País', 'Visitantes']) +
      tabla('De dónde vienen', origenes, ['Origen / medio', 'Sesiones']) +
      tabla('Páginas más vistas', paginas, ['Ruta', 'Vistas']) +
      tabla('Qué han hecho (eventos)', eventos, ['Evento', 'Veces']) +
      (proyectos.length ? tabla('Qué proyecto han mirado', proyectos, ['Proyecto', 'Veces']) : '') +
      '<p style="font-size:12px;color:#6B6153;margin-top:26px;border-top:1px solid #E4DFD4;padding-top:12px">' +
        'Solo cuentan visitas que aceptaron cookies. El recorrido visitante por visitante no está en la API de GA4 ' +
        '(necesita BigQuery o un logger propio). Las cifras de ayer pueden ajustarse ligeramente durante el día.</p>' +
    '</div>';

  MailApp.sendEmail({ to: MAIL_TO, subject: 'Algoryme · analítica de ayer (' + diaEs + ')', htmlBody: html });
}
