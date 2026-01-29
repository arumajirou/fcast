$ErrorActionPreference = "Stop"
$dist = "dist"
$archive = Join-Path $dist "archive"
New-Item -ItemType Directory -Force -Path $archive | Out-Null

$latest = Join-Path $dist "fcast_latest.zip"
if (Test-Path $latest) {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $old = Join-Path $archive ("fcast_" + $ts + ".zip")
  Move-Item $latest $old
}

# zip current project (exclude dist, reports, lake, venv)
$exclude = @("dist\", "reports\", "forecast_lake\", ".venv\", "__pycache__\", ".git\")
$items = Get-ChildItem -Recurse -File | Where-Object {
  $p = $_.FullName
  foreach ($e in $exclude) { if ($p -like "*\$e*") { return $false } }
  return $true
}

# use .NET ZipFile
Add-Type -AssemblyName System.IO.Compression.FileSystem
if (Test-Path $latest) { Remove-Item $latest -Force }
$zip = [System.IO.Compression.ZipFile]::Open($latest, "Create")
foreach ($f in $items) {
  $rel = Resolve-Path $f.FullName | ForEach-Object { $_.Path.Substring((Resolve-Path ".").Path.Length + 1) }
  [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $f.FullName, $rel) | Out-Null
}
$zip.Dispose()

# keep last 5 archives
$max = 5
$zips = Get-ChildItem $archive -Filter "*.zip" | Sort-Object LastWriteTime -Descending
if ($zips.Count -gt $max) {
  $zips | Select-Object -Skip $max | Remove-Item -Force
}
Write-Host "OK: $latest (archives kept: $max)"
