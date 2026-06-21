Deployment to Google Cloud Run (free tier guidance)

Files added:
- `Dockerfile` — containerizes the Flask app (listens on port 8080)
- `.dockerignore` — keeps build context small
- `.github/workflows/cloud-run-deploy.yml` — GitHub Actions workflow to build and deploy

Quick steps (summary):

1. Create a GCP project and enable Cloud Run & Container Registry or Artifact Registry.
2. Create a service account with `Cloud Run Admin`, `Storage Admin` (or `Artifact Registry Writer`), and `Service Account User` roles. Create and download a JSON key.
3. In your GitHub repository, go to Settings → Secrets → Actions and add:
   - `GCP_PROJECT` — your GCP project id
   - `GCP_REGION` — e.g. `us-central1`
   - `GCP_SA_KEY` — contents of the service account JSON key
4. Push your code to `main`. The workflow will build and deploy to Cloud Run.

Notes about free tier:
- Cloud Run has an always-free allocation (e.g., 180,000 vCPU-seconds and 360,000 GiB-seconds per month) but usage beyond that is billed. Monitor the GCP Free Tier limits.
- If you prefer a fully free static hosting (for only static files), consider Cloudflare Pages — but this app requires a server (Flask), so Cloud Run is recommended.

If you'd like, I can also provide a `Dockerfile` tailored for Cloudflare Workers (as a static site) or create a GitHub Actions workflow for Cloudflare Pages.
