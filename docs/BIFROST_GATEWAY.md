# Secured Bifrost gateway for the VeriFact demo

This setup is a **zero-cost, temporary hackathon demo topology**, not a 24/7 production hosting design. It runs Bifrost on the project owner's laptop and exposes only the inference endpoint through Cloudflare Tunnel. Keep the laptop, Bifrost, the proxy, and the tunnel online while the hosted Vercel app needs AI assessment.

For always-on production use, move Bifrost and its durable configuration store to a managed VM/container host with TLS, persistent storage, authentication, monitoring, and backups. Render's free web services are not suitable for this gateway: they spin down after 15 minutes of inactivity and have ephemeral filesystems.

## Components

- Bifrost (by Maxim AI): local model gateway on `127.0.0.1:8080`; its dashboard and admin API are never exposed publicly.
- `scripts/bifrost_proxy.py`: local allow-list proxy on `127.0.0.1:8081`; accepts only authenticated `POST /v1/chat/completions`, limits request size, and only permits `gemini/` model routes.
- Cloudflare Quick Tunnel: exposes the proxy's port only. The random `trycloudflare.com` hostname changes when the tunnel restarts.
- Vercel environment variables: `BIFROST_BASE_URL` is the tunnel root URL, `BIFROST_API_KEY` is the proxy bearer token, and `BIFROST_MODEL` is `gemini/gemini-3.5-flash-lite`.

## First-time Bifrost setup

1. Start Bifrost locally with a setup token and a persistent app directory. Do not bind it to a public interface.
2. Open `http://127.0.0.1:8080` locally and create the first administrator account. Paste the one-time setup token when prompted; choose and keep your own admin password.
3. In **Models → Model Providers**, add **Google Gemini**, create a key, and paste a Gemini API key directly into Bifrost. Do not put the key in GitHub, Vercel, or ChatGPT.
4. Restrict allowed models to `gemini-3.5-flash-lite` where possible and save.
5. Create a Bifrost virtual key for the app and allow only `gemini-3.5-flash-lite` for that virtual key. The provider key may have broader model availability, but the app virtual key should remain model-restricted.
6. Test the route locally using model `gemini/gemini-3.5-flash-lite` at `/v1/chat/completions`.

The Gemini free tier is suitable for a limited prototype but Google states that free-tier content may be used to improve its products. Only send public/demo content through this route. See Google's current [Gemini API pricing and data-use terms](https://ai.google.dev/gemini-api/docs/pricing).

## Proxy and tunnel

1. Generate a random bearer token and store it at `~/.config/verifact/bifrost_proxy_token` with permissions `0600`.
2. Start `python3 scripts/bifrost_proxy.py`. Verify `GET http://127.0.0.1:8081/healthz` returns 200, unauthenticated inference returns 401, and `/api/providers` returns 404.
3. Start `cloudflared tunnel --url http://127.0.0.1:8081` and copy the generated HTTPS `trycloudflare.com` root URL.
4. Set Vercel Production environment variables:
   - `BIFROST_BASE_URL`: the generated HTTPS tunnel root URL
   - `BIFROST_API_KEY`: the local proxy bearer token (sensitive)
   - `BIFROST_MODEL`: `gemini/gemini-3.5-flash-lite`
5. Redeploy Vercel. Confirm `/health` reports `bifrost_configured: true` and run a live verification test. The tunnel URL becomes invalid when the tunnel process stops.

## Security boundaries

- Never tunnel port 8080 directly. That would expose the Bifrost dashboard and administrative APIs.
- Keep Bifrost bound to loopback. The tunnel targets only the proxy on loopback port 8081.
- The proxy checks a 256-bit random bearer token, allows only one inference path, restricts routes to the `gemini/` provider namespace, caps request size, and does not log claim text or authorization headers. Bifrost virtual-key policy further restricts the enabled app route to `gemini-3.5-flash-lite`.
- Rotate the proxy token if it is exposed. Keep provider keys inside Bifrost's local configuration and do not commit the Bifrost app directory.
- This is a demo bridge. It is not a substitute for a managed, always-on gateway with a stable hostname and hardened operational controls.
