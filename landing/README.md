# SecureCode Landing Page

A framework-free GitHub Pages site for the SecureCode local-first Python scanner. It is built with plain HTML, CSS, and a small vanilla JavaScript enhancement; it does not connect to the analyzer API or collect submitted source.

## Files

- `index.html` - page content and metadata
- `styles.css` - responsive layout and visual styles
- `script.js` - progressive enhancement for smooth in-page navigation

## Local preview

From this directory, run a static HTTP server with Python 3:

```bash
python3 -m http.server 8080
```

Then open <http://127.0.0.1:8080/>. You can also open `index.html` directly in a browser.

## GitHub Pages

The repository includes `.github/workflows/deploy-landing-pages.yml`, which publishes only this folder as a GitHub Pages artifact when changes are pushed to `main`. In repository **Settings > Pages**, set the build and deployment source to **GitHub Actions**. Push to `main` or run the workflow manually from the **Actions** tab. The project site URL will normally be:

`https://stardustpelt.github.io/secure-code/`
