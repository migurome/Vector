# Clona (o actualiza) los repos listados en repos.txt dentro de third_party/.
# Uso:  powershell -ExecutionPolicy Bypass -File scripts\clone_repos.ps1
# Clon superficial (--depth 1) para ahorrar disco; quitar --depth si se necesita el historial.
$root = Split-Path $PSScriptRoot -Parent
$dest = Join-Path $root 'third_party'
New-Item -ItemType Directory -Force $dest | Out-Null

foreach ($line in Get-Content (Join-Path $root 'repos.txt')) {
    $repo = $line.Trim()
    if (-not $repo -or $repo.StartsWith('#')) { continue }
    $dir = Join-Path $dest ($repo -replace '/', '__')
    if (Test-Path (Join-Path $dir '.git')) {
        Write-Host "Actualizando $repo"
        git -C $dir pull --ff-only
    } else {
        Write-Host "Clonando $repo"
        # longpaths: wire-os-victor tiene rutas > 260 caracteres que Windows rechaza por defecto
        git clone --depth 1 -c core.longpaths=true "https://github.com/$repo.git" $dir
    }
    if ($LASTEXITCODE -ne 0) { Write-Warning "Fallo con $repo" }
}
