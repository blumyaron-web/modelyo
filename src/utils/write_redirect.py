"""Write a meta-refresh index.html at the root of the Allure report dir."""
import pathlib, sys

report_root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "reports/allure-report")
subdir = "awesome" if (report_root / "awesome/index.html").exists() else "."
html = f"""<!DOCTYPE html>
<html>
  <head><meta http-equiv="refresh" content="0; url=./{subdir}/index.html" /></head>
  <body><a href="./{subdir}/index.html">Open report</a></body>
</html>"""
(report_root / "index.html").write_text(html)
print(f"redirect written -> ./{subdir}/index.html")
