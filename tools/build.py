"""Builds ../index.html as ONE self-contained file (CSS, JS, data and images inlined).
Run after editing css/, js/ or images/:  python3 tools/build.py"""
import base64, glob, json, os, re
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
rd = lambda p: open(os.path.join(H, p)).read()
img = {os.path.basename(f)[:-4]: "data:image/svg+xml;base64," + base64.b64encode(open(f, "rb").read()).decode()
       for f in sorted(glob.glob(os.path.join(H, "images", "*.svg")))}
t = rd("tools/index.template.html")
t = t.replace('<link rel="stylesheet" href="css/styles.css">', "<style>" + rd("css/styles.css") + "</style>")
t = re.sub(r'src="images/(hero\d)\.svg"', lambda m: f'src="{img[m.group(1)]}"', t)
js = "const IMG=" + json.dumps(img) + ";\n" + "\n".join(rd(f"js/{n}.js") for n in ("config", "data", "app"))
tag = '<script src="js/config.js"></script><script src="js/data.js"></script><script src="js/app.js"></script>'
assert tag in t
t = t.replace(tag, "<script>\n" + js + "\n</script>")
open(os.path.join(H, "index.html"), "w").write(t)
print("index.html", round(len(t) / 1024), "KB")
