# Render Deployment

The repository-root `render.yaml` defines a Python web service rooted at `backend/`. It installs dependencies, collects static files, applies database migrations, and starts Gunicorn through `securecode_web.wsgi:application`.

## Blueprint Setup

Create a Render Blueprint from the repository and provide these prompted values:

- `DATABASE_URL`: the internal connection URL for a PostgreSQL database. Production settings reject SQLite when `DJANGO_DEBUG` is disabled.
- `DJANGO_CORS_ORIGINS`: the exact frontend origin, such as `https://your-app.vercel.app`. Separate multiple origins with commas; wildcard origins are not enabled.

Render generates `DJANGO_SECRET_KEY` and supplies `RENDER_EXTERNAL_HOSTNAME`, which is included in `ALLOWED_HOSTS`. To use a custom backend domain, add it to `DJANGO_ALLOWED_HOSTS` in the Render service environment as a comma-separated host list.

The Blueprint uses Render's free web-service plan, which may spin down when idle. For an always-on production service, select an appropriate paid plan in Render. The Blueprint expects a separately provisioned PostgreSQL database and does not create one.

## Security Notes

`DEBUG` is disabled, HTTPS redirect, one-year HSTS for the service and its subdomains, and secure session/CSRF cookies are enabled by the Render environment. Browser HSTS preload is not enabled automatically because it requires a deliberate domain-ownership decision. Static files are served by WhiteNoise. CORS only allows origins explicitly provided in `DJANGO_CORS_ORIGINS`.

The analysis API currently has no user authentication or rate limiting. CORS is not access control; before accepting untrusted public traffic, add and review suitable abuse protections. Keep `DATABASE_URL` and any custom secrets in Render's environment settings, not in the repository.
