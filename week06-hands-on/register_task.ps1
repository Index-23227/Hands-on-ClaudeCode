# Week06 파이프라인을 Windows 작업 스케줄러에 등록
# 관리자 권한 PowerShell에서 실행하세요.
#
# 해제하려면:
#   Unregister-ScheduledTask -TaskName Week06Pipeline -Confirm:$false

$ErrorActionPreference = "Stop"

$TaskName   = "Week06Pipeline"
$RepoRoot   = Split-Path -Parent $MyInvocation.MyCommand.Path
$PipelineSrc = Join-Path $RepoRoot "run_pipeline.py"
$WorkingDir  = $RepoRoot

# run_pipeline.py 존재 확인
if (-not (Test-Path $PipelineSrc)) {
    throw "run_pipeline.py 가 없습니다: $PipelineSrc"
}

# Python 실행 파일 찾기 (py.exe 우선, 없으면 python.exe)
$PyPath = $null
foreach ($exe in @("py.exe", "python.exe")) {
    $cmd = Get-Command $exe -ErrorAction SilentlyContinue
    if ($cmd) { $PyPath = $cmd.Source; break }
}
if (-not $PyPath) {
    throw "Python 실행 파일(py.exe 또는 python.exe)을 PATH에서 찾지 못했습니다."
}

Write-Host "등록 내용:"
Write-Host "  Task Name : $TaskName"
Write-Host "  Python    : $PyPath"
Write-Host "  Script    : $PipelineSrc"
Write-Host "  WorkingDir: $WorkingDir"
Write-Host "  Trigger   : 매일 10:57"
Write-Host ""

$Action = New-ScheduledTaskAction `
    -Execute $PyPath `
    -Argument "`"$PipelineSrc`"" `
    -WorkingDirectory $WorkingDir

$Trigger = New-ScheduledTaskTrigger -Daily -At 10:50am

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

# 이미 등록돼 있으면 덮어쓰기
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "기존 등록이 있어 해제 후 재등록합니다."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Week06 자동화 파이프라인 (매일 환율+매출 갱신)"

Write-Host ""
Write-Host "등록 완료! 지금 바로 한 번 돌려보려면:"
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "해제하려면:"
Write-Host "  Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
