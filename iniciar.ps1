param([switch]$Diagnostico)
$ErrorActionPreference = 'Stop'
if ($Diagnostico) {
    & (Join-Path $PSScriptRoot 'herramientas.ps1') -Accion doctor
    exit
}
& (Join-Path $PSScriptRoot 'herramientas.ps1') -Accion python -Argumentos @('tools/run.py', 'start')
