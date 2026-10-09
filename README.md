# Dishpatch
Food delivery website: static frontend + serverless backend (API Gateway, Lambda, DynamoDB).

Run locally: open `index.html` (one self-contained file; orders are simulated while `API_URL` is empty).

Deploy
1. `sam build && sam deploy --guided`, then copy the `ApiUrl` output.
2. Paste it into `js/config.js`, then run `python3 tools/build.py` to rebuild `index.html` (or edit `window.API_URL` directly inside `index.html`).
3. Upload just `index.html` to an S3 bucket with static website hosting (or AWS Amplify Hosting).

Customise: edit restaurants and dishes in `js/data.js`, then run `python3 tools/make_images.py` to draw pictures for any new ones.
