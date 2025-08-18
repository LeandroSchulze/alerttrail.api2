# AlertTrail API — Suite v7
Incluye TODO lo anterior + novedades:
- **/metrics** con **etiquetas** (plan/rol) y métricas legacy para compatibilidad.
- Toggle de **cookies seguras** con `SECURE_COOKIES=true` (útil en prod con HTTPS).
- **Docker Compose** listo con **Prometheus** y **Grafana**.
- Mantiene: importador CSV, rate limit en login y analyze, export CSV, PDF, IA (Pro), paginación configurable.

## Rápido con Docker Compose
```bash
cp .env.sample .env   # y ajustá valores
docker compose up --build
```
Servicios:
- App: http://localhost:8000  (metrics en `/metrics`)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  (user: admin / pass: admin)

## Variables .env
Ver `.env.sample`. Principales:
- `SECRET_KEY` (cámbiala!)
- `SECURE_COOKIES=true` para prod.
- `VERSION`, `GIT_COMMIT`
- Rate limits:
  - login: `RATE_LIMIT_MAX`, `RATE_LIMIT_WINDOW`
  - analyze: `RATE_LIMIT_UPLOAD_MAX`, `RATE_LIMIT_UPLOAD_WINDOW`

## Métricas (Prometheus)
- `alerttrail_analyses_total` (legacy, sin etiquetas)
- `alerttrail_pdf_downloads_total` (legacy)
- `alerttrail_login_rate_limited_total` (legacy)
- `alerttrail_upload_rate_limited_total` (legacy)
- `alerttrail_uptime_seconds` (gauge)
- **Nuevas con etiquetas**:
  - `alerttrail_analyses_total_labeled{plan,role}`
  - `alerttrail_pdf_downloads_total_labeled{plan,role}`
  - `alerttrail_requests_rate_limited_total{type="login|upload"}`

## Scripts incluidos
- `create_user.py` — crear/actualizar un usuario
- `import_users_csv.py` — carga masiva desde CSV

