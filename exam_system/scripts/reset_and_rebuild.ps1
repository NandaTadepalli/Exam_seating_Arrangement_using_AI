<#
PowerShell helper to drop and recreate the `exam_db`, run Django migrations and import users from CSV.
USAGE (from project root):
    .\exam_system\scripts\reset_and_rebuild.ps1 -CsvPath ".\data\users.csv"

WARNING: This script will permanently DROP the database named `exam_db`. Run only on development/test environments.
#>
param(
    [string]$CsvPath
)

Write-Host "*** WARNING: This will DROP and RECREATE the 'exam_db' database. This is DESTRUCTIVE. ***" -ForegroundColor Yellow
$confirm = Read-Host "Type YES to continue"
if ($confirm -ne 'YES') {
    Write-Host "Aborting." -ForegroundColor Cyan
    exit 1
}

# Path to SQL file that drops/creates DB
$sqlFile = Join-Path -Path $PSScriptRoot -ChildPath "..\sql\drop_create_db.sql"
$sqlFile = (Resolve-Path $sqlFile).ProviderPath
if (-not (Test-Path $sqlFile)) {
    Write-Host "SQL file not found: $sqlFile" -ForegroundColor Red
    exit 1
}

# Run the SQL to drop/create DB. mysql client must be in PATH.
Write-Host "Preparing to run SQL to drop/create DB." -ForegroundColor Green
# Find mysql.exe on PATH
$mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
if ($null -eq $mysqlCmd) {
    Write-Host "MySQL client ('mysql') was not found on PATH." -ForegroundColor Yellow
    $mysqlPath = Read-Host "Enter full path to mysql.exe (or press Enter to skip and run SQL manually)"
    if ([string]::IsNullOrWhiteSpace($mysqlPath)) {
        Write-Host "No mysql client provided. Please run the SQL file manually in MySQL Workbench or install MySQL client and re-run this script." -ForegroundColor Red
        Write-Host "SQL file path: $sqlFile" -ForegroundColor Cyan
        exit 1
    }
    if (-not (Test-Path $mysqlPath)) {
        Write-Host "Provided mysql.exe path not found: $mysqlPath" -ForegroundColor Red
        exit 1
    }
    $mysqlExe = (Resolve-Path $mysqlPath).ProviderPath
} else {
    $mysqlExe = $mysqlCmd.Path
}

Write-Host "Running: $mysqlExe -u root -p < $sqlFile (via cmd.exe)" -ForegroundColor Green
# Use cmd.exe /c so the shell input redirection '<' works on Windows PowerShell
$cmd = '"' + $mysqlExe + '" -u root -p < "' + $sqlFile + '"'
# Pass the entire '/c <command>' as a single argument so cmd.exe properly parses quoted paths with spaces
Start-Process -FilePath cmd.exe -ArgumentList "/c $cmd" -NoNewWindow -Wait
if ($LASTEXITCODE -ne 0) {
    Write-Host "MySQL command failed (exit code $LASTEXITCODE). Aborting." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Optionally install requirements (uncomment if you want this automated)
# Write-Host "Installing Python requirements..."
# python -m pip install -r requirements.txt

# Run Django migrations
Write-Host "Running Django migrations..." -ForegroundColor Green
python manage.py makemigrations
if ($LASTEXITCODE -ne 0) { Write-Host "makemigrations failed" -ForegroundColor Red; exit $LASTEXITCODE }

python manage.py migrate
if ($LASTEXITCODE -ne 0) { Write-Host "migrate failed" -ForegroundColor Red; exit $LASTEXITCODE }

# Import users CSV
if (-not $CsvPath) {
    $CsvPath = Read-Host "Enter path to users CSV file (columns: username,email,password,user_id,...)"
}

if (-not (Test-Path $CsvPath)) {
    Write-Host "CSV file not found: $CsvPath" -ForegroundColor Red
    exit 1
}

Write-Host "Importing users from: $CsvPath" -ForegroundColor Green
python manage.py import_users "$CsvPath"
if ($LASTEXITCODE -ne 0) { Write-Host "import_users failed" -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "Done. Verify accounts_user table and run your app." -ForegroundColor Cyan
Write-Host "Example verification (you'll be prompted for MySQL password):" -ForegroundColor Cyan
Write-Host "mysql -u root -p -D exam_db -e \"SHOW CREATE TABLE accounts_user\G\""

exit 0
