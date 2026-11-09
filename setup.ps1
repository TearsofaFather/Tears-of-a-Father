# Tears of a Father render kit: one-time setup + comparison test.
# Installs Python, Git and ffmpeg (via winget) if missing, downloads the kit and the Kokoro v1.0 voice model,
# verifies the model's checksum, then renders the comparison passage and uploads it.
$ErrorActionPreference = 'Stop'
$Dir = Join-Path $env:USERPROFILE 'TearsRender'
$Repo = 'https://github.com/TearsofaFather/Tears-of-a-Father.git'
function Refresh-Path { $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') }
function Need($cmd, $id) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Host "Installing $id ..." -ForegroundColor Cyan
    winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
  }
}
Need git 'Git.Git'
Need ffmpeg 'Gyan.FFmpeg'
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { Need py 'Python.Python.3.13' }
Refresh-Path
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  $ff = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($ff) { $env:Path += ';' + $ff.DirectoryName; [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';' + $ff.DirectoryName, 'User') }
}
if (Test-Path "$Dir\.git") { git -C $Dir pull --rebase origin render-kit } else { git clone --branch render-kit --single-branch $Repo $Dir }
Set-Location $Dir
if (-not (git config user.name)) { git config user.name 'Tears render PC' }
if (-not (git config user.email)) { git config user.email 'render-pc@users.noreply.github.com' }
if (-not (Test-Path "$Dir\venv")) { py -3.13 -m venv "$Dir\venv" }
& "$Dir\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$Dir\venv\Scripts\python.exe" -m pip uninstall -y onnxruntime-directml onnxruntime 2>$null
& "$Dir\venv\Scripts\python.exe" -m pip install numpy scipy "onnxruntime-gpu[cuda,cudnn]"
New-Item -ItemType Directory -Force "$Dir\models" | Out-Null
$files = @{
  'kokoro-v1.0.onnx' = '7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5'
  'voices-v1.0.bin'  = 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'
}
foreach ($f in $files.Keys) {
  $p = "$Dir\models\$f"
  if (-not (Test-Path $p) -or (Get-FileHash $p -Algorithm SHA256).Hash.ToLower() -ne $files[$f]) {
    Write-Host "Downloading $f ..." -ForegroundColor Cyan
    curl.exe -L -o $p "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
  }
  if ((Get-FileHash $p -Algorithm SHA256).Hash.ToLower() -ne $files[$f]) { throw "$f did not match the expected checksum; stopping." }
}
Write-Host 'Model verified. Rendering the comparison passage...' -ForegroundColor Green
& "$Dir\venv\Scripts\python.exe" run.py test
