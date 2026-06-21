RitsSite Release v0.1.0

What's included:
- Initial production-ready packaging of the Flask site.
- `requirements.txt` includes `gunicorn`.
- `Procfile` present for Heroku-style deployment.
- Standardized logos moved to `static/images/` (`Ritslog.png`, `RitsLogoLight3.png`).
- Removed temporary fallback mappings in `app.py`.

Notes:
- The `Images/` folder contains legacy/untracked image files; release includes only tracked `static/` assets.
- To deploy on Heroku: `git push heroku main` (configure `SECRET_KEY` and other env vars).

Build created: `dist/RitsSite-v0.1.0.zip` (git archive of current `HEAD`).
