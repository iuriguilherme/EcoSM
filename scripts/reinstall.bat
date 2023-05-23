@echo "Reinstalling ecorcon"
git pull origin main & Remove-Item "./venv" -Recurse & python -m pip --user --upgrade pip pipenv & python -m pipenv --rm
