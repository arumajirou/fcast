$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path "reports\pytest" | Out-Null
$env:PYTHONPATH = "src"
pytest -q --html=reports\pytest\report.html --self-contained-html
Write-Host "OK: reports\pytest\report.html"
