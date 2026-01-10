cd C:\Users\sande\code\FLL-Unearthed-2025-2026
copy "C:\Users\sande\Documents\LEGO Education SPIKE\FLL Unearthed\*.*" .
git pull origin main
git add .
git commit -m "Describe your changes clearly"
git pull origin main --rebase
git push origin main