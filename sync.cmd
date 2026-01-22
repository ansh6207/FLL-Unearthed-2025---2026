@echo off
REM FLL GitHub Sync Script
REM Run from repo root: sync.cmd

setlocal enabledelayedexpansion

REM Get repo root (current directory)
cd /d "%~dp0"

REM Verify we're in a git repository
if not exist .git (
    echo Error: This script must be run from the scripts folder in a Git repository.
    echo Current directory: %cd%
    pause
    exit /b 1
)

REM Get the device name
for /f "delims=" %%A in ('hostname') do set DEVICE_NAME=%%A
set BRANCH_NAME=sync/%DEVICE_NAME%/%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%
set BRANCH_NAME=%BRANCH_NAME: =0%

echo.
echo ============================================
echo FLL GitHub Sync - %DEVICE_NAME%
echo ============================================
echo.

REM Always run extraction to keep extracted Python code in sync with LLSP3 files
echo Extracting Python code from LLSP3 files...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0scripts\extract-llsp3.ps1' -RepoRoot '%cd%'"
echo.

REM Fetch latest changes from remote
git fetch origin

REM Stage any extracted files
git add -A

REM Check if there are local changes to commit
git diff-index --quiet HEAD --
if errorlevel 1 (
    REM Stage and commit local changes
    git add .
    git commit -m "Sync from %DEVICE_NAME% - %date% %time%"
    
    REM Try to merge main into current branch
    git merge origin/main
    
    REM Check if merge resulted in conflicts
    git diff --name-only --diff-filter=U >nul 2>&1
    if not errorlevel 1 (
        REM No conflicts - push to main directly
        echo No conflicts detected. Pushing to main...
        git push origin main
    ) else (
        REM Conflicts detected - resolve binary files automatically by keeping ours
        echo Merge conflicts detected. Resolving binary file conflicts...
        
        REM Get list of conflicted files
        for /f "delims=" %%F in ('git diff --name-only --diff-filter=U') do (
            REM Check if file is binary (.llsp3, .py compiled files, etc)
            set FILE=%%F
            if "!FILE:~-6!"==".llsp3" (
                echo Resolving binary conflict in !FILE! - keeping local version...
                git checkout --ours "!FILE!"
                git add "!FILE!"
            )
        )
        
        REM Check if there are still unresolved conflicts
        git diff --name-only --diff-filter=U >nul 2>&1
        if errorlevel 1 (
            REM Still have text file conflicts - create branch for manual review
            echo Text file conflicts still present. Creating branch for manual review...
            
            REM Abort the merge to return to clean state
            git merge --abort
            
            REM Create and checkout new branch
            git checkout -b %BRANCH_NAME%
            
            REM Push the branch with the new changes (before merge attempt)
            git add .
            git push -u origin %BRANCH_NAME%
            
            echo.
            echo MERGE CONFLICT HANDLING:
            echo - Branch created: %BRANCH_NAME%
            echo - Push to GitHub to create a Pull Request
            echo - Please review and manually merge conflicts
            echo - Visit: https://github.com/ansh6207/FLL-Unearthed-2025---2026/tree/%BRANCH_NAME%
        ) else (
            REM All conflicts resolved - complete the merge
            echo All conflicts resolved. Completing merge...
            git commit -m "Merge origin/main - auto-resolved binary conflicts"
            git push origin main
        )
    )
) else (
    echo No new local changes to commit.
    
    REM However, check if branch is ahead of origin and push if needed
    git rev-list --count origin/main..HEAD >nul 2>&1
    if not errorlevel 1 (
        echo Your branch is ahead of origin/main. Pushing commits...
        git push origin main
    )
)

REM Sync with latest main
git fetch origin
git checkout main
git pull origin main

echo.
echo ============================================
echo Sync completed successfully!
echo ============================================
echo.
pause
