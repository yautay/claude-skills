#!/usr/bin/env bash
# git-clean report — uruchamia report.py pierwszym działającym Pythonem 3.8+.
# (Na Windowsie `python3` bywa atrapą ze Sklepu, która nic nie robi, a Python
# bywa dostępny wyłącznie przez uv albo venv repozytorium.)
# Kolejność: $GIT_CLEAN_PYTHON, python3, python, py -3, `uv python find`,
# venv repozytorium (.venv), typowe instalacje Windows (python.org, uv).
# Użycie: report.sh [argumenty report.py]

DIR=$(cd "$(dirname "$0")" && pwd)
ARGS=("$@")
TRIED=()

try_py() {  # $@ = komenda interpretera; przy sukcesie nie wraca (exec)
  TRIED+=("$*")
  "$@" -c 'import sys; sys.exit(sys.version_info < (3, 8))' >/dev/null 2>&1 || return 1
  PYTHONUTF8=1 exec "$@" "$DIR/report.py" "${ARGS[@]}"
}

[ -n "${GIT_CLEAN_PYTHON:-}" ] && try_py "$GIT_CLEAN_PYTHON"
for py in python3 python; do
  command -v "$py" >/dev/null 2>&1 && try_py "$py"
done
command -v py >/dev/null 2>&1 && try_py py -3
if command -v uv >/dev/null 2>&1; then
  uvpy=$(uv python find '>=3.8' 2>/dev/null) && [ -n "$uvpy" ] && try_py "$uvpy"
fi
top=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -n "$top" ]; then
  for venv in "$top/.venv/Scripts/python.exe" "$top/.venv/bin/python"; do
    [ -x "$venv" ] && try_py "$venv"
  done
fi
if command -v cygpath >/dev/null 2>&1; then
  for base in "${LOCALAPPDATA:-}" "${APPDATA:-}"; do
    [ -n "$base" ] || continue
    base=$(cygpath -u "$base")
    for cand in "$base"/Programs/Python/Python3*/python.exe "$base"/uv/python/cpython-3*/python.exe; do
      [ -x "$cand" ] && try_py "$cand"
    done
  done
fi

echo "BŁĄD: brak Pythona 3.8+ — raport HTML niedostępny (audyt i sync działają bez niego)" >&2
echo "Sprawdzono: ${TRIED[*]:-(nic nie znaleziono)}" >&2
echo "Wskaż interpreter: GIT_CLEAN_PYTHON=/ścieżka/do/python bash report.sh ..." >&2
exit 3
