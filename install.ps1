# AI Documentary Video-Making Studio Skill (v4.0) — Windows 1-Click Installer
# Usage: irm https://raw.githubusercontent.com/gmakercodeby-arch/ai-documentary-video-studio-skill/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/gmakercodeby-arch/ai-documentary-video-studio-skill.git"
$SkillName = "ai-documentary-studio"

$Targets = @(
    (Join-Path $HOME ".gemini\config\skills\$SkillName")
)
if (Test-Path (Join-Path $HOME ".claude")) {
    $Targets += (Join-Path $HOME ".claude\skills\$SkillName")
}
if (Test-Path (Join-Path $HOME ".cursor")) {
    $Targets += (Join-Path $HOME ".cursor\skills\$SkillName")
}

Write-Host "`n=== AI Documentary Video-Making Studio Skill (v4.0) — 1-Click Install ===" -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is required. Install Git from https://git-scm.com/ and re-run."
    exit 1
}

$Primary = $Targets[0]
New-Item -ItemType Directory -Force -Path (Split-Path $Primary -Parent) | Out-Null

if (Test-Path $Primary) {
    Write-Host "[1/3] Updating existing skill in $Primary ..." -ForegroundColor Yellow
    git -C $Primary pull --ff-only
} else {
    Write-Host "[1/3] Cloning skill into $Primary ..." -ForegroundColor Green
    git clone --depth 1 $RepoUrl $Primary
}

for ($i = 1; $i -lt $Targets.Count; $i++) {
    $t = $Targets[$i]
    New-Item -ItemType Directory -Force -Path (Split-Path $t -Parent) | Out-Null
    if (Test-Path $t) { Remove-Item -Recurse -Force $t }
    Copy-Item -Recurse -Force $Primary $t
    Write-Host "      Synced skill to $t" -ForegroundColor DarkGray
}

# Also install bundled companion skill: gmz-viral-topic-hunter
$HunterSrc = Join-Path $Primary "skills\gmz-viral-topic-hunter"
if (Test-Path $HunterSrc) {
    $HunterTargets = @((Join-Path $HOME ".gemini\config\skills\gmz-viral-topic-hunter"))
    if (Test-Path (Join-Path $HOME ".claude")) { $HunterTargets += (Join-Path $HOME ".claude\skills\gmz-viral-topic-hunter") }
    if (Test-Path (Join-Path $HOME ".cursor")) { $HunterTargets += (Join-Path $HOME ".cursor\skills\gmz-viral-topic-hunter") }
    foreach ($ht in $HunterTargets) {
        New-Item -ItemType Directory -Force -Path (Split-Path $ht -Parent) | Out-Null
        if (Test-Path $ht) { Remove-Item -Recurse -Force $ht }
        Copy-Item -Recurse -Force $HunterSrc $ht
    }
    Write-Host "      Installed companion skill: gmz-viral-topic-hunter" -ForegroundColor DarkGray
}

Write-Host "[2/3] Installing Python dependencies..." -ForegroundColor Green
$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }
& $py -m pip install --upgrade -r (Join-Path $Primary "requirements.txt")

Write-Host "[3/3] Running Stage-0 Environment & GPU Doctor..." -ForegroundColor Green
& $py (Join-Path $Primary "scripts\check_setup.py")

Write-Host "`nDONE! Skill installed at: $Primary" -ForegroundColor Cyan
Write-Host "Now tell your AI Agent: 'Use ai-documentary-studio to set up my studio and make a documentary!'" -ForegroundColor Yellow
