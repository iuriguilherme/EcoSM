@echo "Reinstalling ecorcon"
git pull origin main & Remove-Item "./venv" -Recurse & rmdir /s /q venv & pip --user --upgrade pip pipenv & python -m pipenv --rm
