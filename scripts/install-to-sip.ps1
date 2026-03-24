param(
    [string]$SipRoot = "C:\Users\rml\source\repos\rimmel73\SIP"
)

$ErrorActionPreference = "Stop"

$pluginSource = Join-Path $PSScriptRoot "..\plugin\sip_touch_ui.py"
$manifestSource = Join-Path $PSScriptRoot "..\plugin\sip_touch_ui.manifest"
$templateSource = Join-Path $PSScriptRoot "..\templates\sip_touch_ui.html"

$pluginTarget = Join-Path $SipRoot "plugins\sip_touch_ui.py"
$manifestTarget = Join-Path $SipRoot "plugins\manifests\sip_touch_ui.manifest"
$templateTarget = Join-Path $SipRoot "templates\sip_touch_ui.html"

Copy-Item $pluginSource $pluginTarget -Force
Copy-Item $manifestSource $manifestTarget -Force
Copy-Item $templateSource $templateTarget -Force

Write-Host "Installed SIP Touch UI into $SipRoot"
