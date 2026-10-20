# Rebuilds the pack-14 results from the saved data, in order. Offline steps run by default; -Network re-runs the API and download steps (cached, slow, rate-limit dependent).
# Usage: powershell -File rerun.ps1 [-Network]
param([switch]$Network)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path 'D:\')) { throw 'D: is missing - stop.' }
$py   = 'D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe'
$rs   = 'C:\Program Files\R\R-4.5.3\bin\Rscript.exe'
$code = 'D:\Research-Publishing\14-fintech-emissions-meta\code'
function Run($s) { Write-Host "== $s"; & $py -X utf8 (Join-Path $code $s); if ($LASTEXITCODE -ne 0) { throw "$s failed" } }
if ($Network) {
  Run 'search14.py'; Run 'merge_screen1.py'; Run 'enrich_abstracts.py'; Run 'make_fulltext_queue.py'; Run 'fetch_fulltext.py'   # fetch_fulltext.py takes the queue file as an argument; see its docstring
  Run 'fetch_warning_lists.py'; Run 'parse_warning_lists.py'
}
# 1. verify every hand-coded entry against the full text, then build study table and analysis file
Run 'build_estimates.py'; Run 'build_studies.py'
# 2. meta-analysis in R (metafor 5.2.1, clubSandwich 0.7.0 in D:\Research-Publishing\_tools\R-lib)
$env:R_LIBS_USER = 'D:\Research-Publishing\_tools\R-lib'
Push-Location $code; & $rs meta_analysis.R ..\extraction\estimates.csv ..\results\; Pop-Location
# 3. PRISMA counts and figure, venue flags, citation library, reading notes (quotes are checked against the text), double-screen sample and STAGING.md
Run 'prisma14.py'; Run 'venue_flags_all.py'; Run 'build_reading_notes14.py'
if ($Network) { Run 'build_citations14.py'; Run 'network_depth14.py' }
Write-Host 'done'
