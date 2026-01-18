# Extract Python source from LLSP3 files
# This script extracts Python code from all .llsp3 files and saves to src/
# with folder hierarchy maintained

param(
    [string]$RepoRoot = (Get-Location)
)

Write-Host "Extracting Python code from LLSP3 files..." -ForegroundColor Green

# Track which Python files should exist based on current LLSP3 files
$expectedPyFiles = @{}

$llsp3Files = Get-ChildItem -Path $RepoRoot -Filter "*.llsp3" -Recurse

if ($llsp3Files.Count -eq 0) {
    Write-Host "No LLSP3 files found." -ForegroundColor Yellow
} else {
    Write-Host "Found $($llsp3Files.Count) LLSP3 file(s)" -ForegroundColor Cyan
}

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
                    $pyFilePath = Join-Path $targetDir "$baseName.py"
                    Set-Content -Path $pyFilePath -Value $pythonCode -Encoding UTF8 -Force
                    
                    # Track this expected Python file (for later cleanup of orphaned files)
                    $expectedPyFiles[$pyFilePath] = $true
                    
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

# Clean up orphaned Python files (files extracted from deleted LLSP3s)
$srcDir = Join-Path $RepoRoot 'src'
if (Test-Path $srcDir) {
    $allPyFiles = Get-ChildItem -Path $srcDir -Filter "*.py" -Recurse
    foreach ($pyFile in $allPyFiles) {
        if (-not $expectedPyFiles.ContainsKey($pyFile.FullName)) {
            try {
                Remove-Item $pyFile.FullName -Force
                Write-Host "  Deleted orphaned: $($pyFile.FullName.Substring($RepoRoot.Length + 1))" -ForegroundColor Yellow
            }
            catch {
                Write-Host "  Warning: Could not delete $($pyFile.Name): $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host "Python code extracted to src/ directory." -ForegroundColor Green
