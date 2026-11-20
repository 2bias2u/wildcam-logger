# wildcam-logger
assignment 1 for TU Wien course: IaaS/PaaS

## Configuration (environment variables)

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | Database connection, e.g. `postgresql+psycopg2://wildcam:<pw>@192.168.100.22:5432/wildcam` | local SQLite file `wildcam.db` |
| `APP_TITLE` | Title shown on the page and in the browser tab | `Wildcam Logger` |
| `SCRIPT_NAME` | URL prefix the app runs under (read by Gunicorn, e.g. `/sea`) | none, app runs at `/` |

Without `APP_TITLE` and `SCRIPT_NAME` the app behaves exactly as in Task 1.

## Task 2: one codebase, two apps

For Task 2 the app is split into one app for land- and air-based animals and one for sea animals.
Both use the **same image**; they differ only in their configuration:

| | Land & Air | Sea |
|---|---|---|
| `APP_TITLE` | `Wildcam Logger – Land & Air` | `Wildcam Logger – Sea` |
| `SCRIPT_NAME` | `/landair` | `/sea` |
| `DATABASE_URL` | `.../wildcam_landair` | `.../wildcam_sea` |
| Container port | 5001 | 5002 |

- **Separate data:** each app has its own database on the shared PostgreSQL server.
- **Separate URLs:** Traefik routes `/landair` and `/sea` to the matching containers. The prefix is
  not stripped; Gunicorn removes it via `SCRIPT_NAME`, and Flask's `url_for` builds all links
  (form action, redirects) with the prefix automatically.
- **Health checks:** `/landair/health` and `/sea/health` (with `SCRIPT_NAME` set, `/health`
  without prefix is not served).

Changes compared to Task 1:
- `app.py`: new variable `APP_TITLE`, passed to the template
- `templates/index.html`: heading and `<title>` use `{{ title }}`
- `Dockerfile`: base image fully qualified (`docker.io/library/python:3.12-slim`), because Podman
  on Ubuntu has no default registry for short names

Example (Podman):

```bash
podman build -t wildcam-logger .
podman run -d --name wildcam-sea -p 5002:5000 \
  -e APP_TITLE="Wildcam Logger – Sea" \
  -e SCRIPT_NAME=/sea \
  -e DATABASE_URL=postgresql+psycopg2://wildcam:<pw>@192.168.100.22:5432/wildcam_sea \
  wildcam-logger
```
