param(
    [ValidateSet('doctor', 'buscar', 'portales', 'python', 'bun')][string]$Accion = 'doctor',
    [string]$Consulta,
    [string]$Ubicacion = 'Argentina',
    [ValidateSet('freehire')][string]$Fuente = 'freehire',
    [ValidateSet('todas', 'remoto', 'hibrido', 'presencial')][string]$Modalidad = 'remoto',
    [ValidateRange(1, 20)][int]$Limite = 10,
    [string[]]$Argumentos = @()
)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$runtimeFile = Join-Path $PSScriptRoot '.runtime/runtime.local.json'
$python = $null
if (Test-Path -LiteralPath $runtimeFile) {
    $config = Get-Content -LiteralPath $runtimeFile -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($config.python -and (Test-Path -LiteralPath $config.python)) { $python = $config.python }
}
if (-not $python) {
    foreach ($name in @('python', 'python3', 'py')) {
        $candidate = Get-Command $name -ErrorAction SilentlyContinue
        if ($candidate -and $candidate.Source -notlike '*WindowsApps*') { $python = $candidate.Source; break }
    }
}
if (-not $python) { throw 'Instala Python 3.10 o superior y ejecuta python tools/bootstrap.py.' }
$packages = Join-Path $PSScriptRoot '.runtime/python-packages'
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$packages;$env:PYTHONPATH" } else { $packages }
$runArgs = @((Join-Path $PSScriptRoot 'tools/run.py'))
switch ($Accion) {
    'buscar' {
        if ($Ubicacion -notin @('Argentina', 'AR')) { throw 'Esta consulta automatica filtra Argentina; usa el asistente para otros lugares.' }
        if ([string]::IsNullOrWhiteSpace($Consulta)) { throw 'Indica -Consulta con el puesto o habilidad.' }
        $modes = @{todas='all'; remoto='remote'; hibrido='hybrid'; presencial='onsite'}
        $runArgs += @('search', '--query', $Consulta, '--mode', $modes[$Modalidad], '--limit', "$Limite")
    }
    'portales' { $runArgs += 'portals' }
    'doctor' { $runArgs += 'doctor' }
    default { $runArgs += @($Accion, '--'); $runArgs += $Argumentos }
}
& $python @runArgs
if ($LASTEXITCODE -ne 0) { throw "La accion $Accion finalizo con codigo $LASTEXITCODE" }
