import os
import socket
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Ohne DATABASE_URL -> lokale SQLite-Datei, sonst z.B. PostgreSQL auf dem DB-Server
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///wildcam.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Sighting(db.Model):
    __tablename__ = "sightings"
    id = db.Column(db.Integer, primary_key=True)
    animal = db.Column(db.String(100), nullable=False)
    stream = db.Column(db.String(200), nullable=False)
    seen_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    sightings = Sighting.query.order_by(Sighting.seen_at.desc()).all()
    return render_template(
        "index.html",
        sightings=sightings,
        hostname=socket.gethostname(),
        now=datetime.now().strftime("%Y-%m-%dT%H:%M"),
        error=request.args.get("error"),
    )


@app.route("/add", methods=["POST"])
def add():
    animal = request.form.get("animal", "").strip()
    stream = request.form.get("stream", "").strip()
    seen_at = request.form.get("seen_at", "").strip()
    if not animal or not stream or not seen_at:
        return redirect(url_for("index", error="Bitte alle Felder ausfüllen."))
    try:
        seen_at_dt = datetime.strptime(seen_at, "%Y-%m-%dT%H:%M")
    except ValueError:
        return redirect(url_for("index", error="Ungültiger Zeitpunkt."))
    db.session.add(Sighting(animal=animal, stream=stream, seen_at=seen_at_dt))
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    # Für Traefik-Healthchecks in Subtask 1.3
    return {"status": "ok", "host": socket.gethostname()}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
