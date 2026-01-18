# Extract Python source from LLSP3 files
# This script extracts Python code from all .llsp3 files and saves to src/
# with folder hierarchy maintained

param(
    [string]$RepoRoot = (Get-Location)
)

Write-Host "Extracting Python code from LLSP3 files..." -ForegroundColor Green

$llsp3Files = Get-ChildItem -Path $RepoRoot -Filter "*.llsp3" -Recurse

if ($llsp3Files.Count -eq 0) {
    Write-Host "No LLSP3 files found." -ForegroundColor Yellow
    return
}

Write-Host "Found $($llsp3Files.Count) LLSP3 file(s)" -ForegroundColor Cyan

foreach ($file in $llsp3Files) {
    # Calculate relative path from repo root
    $relativePath = $file.FullName.Substring($RepoRoot.Length + 1)
    $lastBackslash = $relativePath.LastIndexOf('\')
    if ($lastBackslash -gt 0) {
        $relativePath = $relativePath.Substring(0, $lastBackslash)
    } else {
        $relativePath = ""
    }
    
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $tempZip = $file.FullName -replace '\.llsp3$', '.zip'
    $tempExtractDir = Join-Path ([System.IO.Path]::GetTempPath()) ("llsp3_temp_" + [System.Guid]::NewGuid().ToString())
    
    try {
        # Create temp directory for extraction
        New-Item -ItemType Directory -Path $tempExtractDir -Force | Out-Null
        
        # Extract LLSP3 (ZIP archive with temp rename)
        Copy-Item $file.FullName $tempZip -Force
        Expand-Archive -Path $tempZip -DestinationPath $tempExtractDir -Force -ErrorAction Stop
        Remove-Item $tempZip -Force
        
        # Extract Python code from projectbody.json
        $projectBody = Join-Path $tempExtractDir 'projectbody.json'
        if (Test-Path $projectBody) {
            try {
                $json = Get-Content $projectBody -Raw | ConvertFrom-Json
                # LEGO Spike stores Python code in the 'main' property
                if ($json.main) {
                    $pythonCode = $json.main
                    
                    # Create src/ folder structure
                    $srcDir = Join-Path $RepoRoot 'src'
                    if ($relativePath) {
                        $targetDir = Join-Path $srcDir $relativePath
                    } else {
                        $targetDir = $srcDir
                    }
                    
                    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                    Set-Content -Path (Join-Path $targetDir "$baseName.py") -Value $pythonCode -Encoding UTF8 -Force
                    Write-Host "  Extracted: src/$relativePath/$baseName.py" -ForegroundColor Cyan
                }
            }
            catch {
                Write-Host "  Warning: Could not parse Python code from $baseName.llsp3" -ForegroundColor Yellow
            }
        }
    }
    catch {
        Write-Host "  Error: Failed to extract $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        # Clean up temp directory
        if (Test-Path $tempExtractDir) {
            Remove-Item $tempExtractDir -Recurse -Force
        }
    }
}

Write-Host "Python code extracted to src/ directory." -ForegroundColor Green
