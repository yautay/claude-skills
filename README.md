# Skills dla Claude i Codexa

Repo przechowuje oddzielne instrukcje dla każdego klienta i samodzielne paczki:

```text
claude/skills/git-clean/   # /git-clean w Claude Code
claude/skills/zlecenie-dev/ # /zlecenie-dev w Claude Code (tylko Claude)
codex/skills/git-clean/    # $git-clean w Codexie
shared/git-clean/          # źródła wspólnych skryptów
claude/skills/repo-safe-data-audit/ # /repo-safe-data-audit w Claude Code
codex/skills/repo-safe-data-audit/  # $repo-safe-data-audit w Codexie
shared/repo-safe-data-audit/        # kanoniczne instrukcje i helper lokalnego LLM
tools/build_skills.py     # pakowanie do katalogów dostawców
tests/                    # testy na tymczasowych repozytoriach
```

Nowy klient może dostać `<klient>/skills/git-clean/SKILL.md`. Skrypt pakujący
odnajduje takie katalogi automatycznie. Każda paczka zawiera wszystkie skrypty;
po instalacji nie zależy od katalogu `shared/` ani API drugiego dostawcy.

## repo-safe-data-audit

Audyt prywatności repozytorium i lokalnie dostępnej historii Git: sekrety,
identyfikujące dane, wyniki pracy i zależności narzędzi. Produkt to prywatny plik
`IMPLEMENTATION-PLAN.md` zapisany **poza repo**, z dokładnymi zadaniami dla
GPT-6.1 Sol medium. Wywołanie skilla niczego nie migruje, nie zmienia historii
i nie publikuje danych. Ręczne odtworzenie remote z czystym pierwszym commitem
jest jedną z planowanych opcji; stare kopie i powierzchnie hostingu wymagają
osobnego rozliczenia. Plan obejmuje też codzienny LAN SFTP backup pięciu
zweryfikowanych punktów odtworzenia i próbę przywrócenia.

- Codex: `codex/skills/repo-safe-data-audit/`, wywołanie `$repo-safe-data-audit`.
- Claude Code: `claude/skills/repo-safe-data-audit/`, `/repo-safe-data-audit`.
- Źródło obu samodzielnych paczek: `shared/repo-safe-data-audit/`.
- Instalacja: skopiuj całą paczkę do katalogu skilli klienta, np.
  `.agents/skills/repo-safe-data-audit/` dla repozytoryjnego Codexa. Przy
  aktualizacji kopii ponownie skopiuj całą paczkę. Nie instaluj samego SKILL.md.

Opcjonalny `local_llm_review.py` pomaga oceniać wcześniej sprawdzone metadane
ścieżek przez lokalny model. Nie zastępuje Gitleaks ani przeglądu treści.
Wymaga jawnego adresu loopback, modelu, potwierdzenia lokalności i bezpiecznych
wejść; wyłącza proxy/przekierowania, waliduje JSON i zapisuje sugestie poza Git.
Nie uruchamia narzędzi modelu. Instrukcje oraz przykład użycia są w paczce,
w `references/local-model-use.md`. Brak runtime'u nie blokuje pozostałego audytu.
Przed użyciem prywatnych danych wyłącz szczegółowe logi i włącz redakcję treści
w runtime. Nie zakładaj oszczędności ani wyższej jakości bez pomiarów.

## zlecenie-dev

Prowadzi zlecenie developerskie od promptu z wymaganiami do scalonej gałęzi:
analiza bez implementacji i plan do akceptacji, batche spisane wg konwencji repo,
segregacja na tory i fazy ze ścieżką krytyczną, orkiestracja osobnych sesji
Claude Code (maks. 3 naraz, każda w swoim worktree i na modelu zaleconym w batchu),
scalanie po jednej gałęzi do gałęzi docelowej i bramka końcowa z pełną suitą.
Stan na żywo pokazuje interaktywny widok HTML (`assets/board.html`), publikowany
jako Artifact z bazą: tory × fazy, kolejka scaleń, dziennik, tabela batchy.

Tylko Claude Code (korzysta z narzędzi sesji, Artifact i ArtifactData desktopowej
aplikacji). Wywołanie: `/zlecenie-dev <wymagania>`, `/zlecenie-dev status`,
`/zlecenie-dev wznów` (po awarii: wznawia przerwane sesje z ich worktree).

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\zlecenie-dev" -Target 'C:\dev\claude-skills\claude\skills\zlecenie-dev'
```

## git-clean — szczegóły

Audyt gałęzi, stashy i worktree, plan sprzątania oraz synchronizacja z gałęzią
domyślną. Rozpoznaje merge, patche po rebase i squash. Pokazuje pracę tylko
lokalną, rozjazdy upstreamu i konflikty z bazą.

Raport HTML zawiera graf DAG z etykietami gałęzi lokalnych, remote, tagów i HEAD,
wybór historii gałęzi, powiększanie, kolorowe oznaczenia kandydatów do usunięcia
i pracy tylko lokalnej, filtrowane tabele, plan A–E oraz migawki „przed → po”.
Graf pokazuje rzeczywistych rodziców commitów: squash/rebase nie tworzy fikcyjnego
połączenia z dawną gałęzią. Równoważność treści jest sprawdzana osobno w tabelach.
Domyślnie pokazuje 120 commitów, maksymalnie 1000. Raport działa offline, bez CDN.

## Bezpieczeństwo

Najpierw raport i podgląd, potem konkretny wybór użytkownika. Sama prośba o audyt
nie oznacza zgody na synchronizację ani kasowanie.

| Blok | Zakres |
|---|---|
| A | lokalne gałęzie z treścią już w bazie |
| B | gałęzie remote — osobna zgoda i świeże dane |
| C | stashe bez osobnej, potrzebnej treści |
| D | prune i gc |
| E | indywidualne decyzje i ratowanie pracy |

Indeks stasha jest sprawdzany osobno od jego drzewa roboczego i plików
nieśledzonych. Jeśli zawiera osobną treść albo nie został sprawdzony w starym
audycie, stash zostaje do oceny. Metadane są kodowane w audycie, komendy cytowane
dla konkretnej powłoki (`--shell bash` / `--shell powershell`). Instrukcje wymagają
ponownej weryfikacji SHA przed mutacją. Nieświeże dane wyłączają blok B.

Nie usuwa się gałęzi bieżącej, domyślnej, chronionej ani wystawionej w worktree.
Chronione: main, master, develop, trunk, release/*, hotfix/*. Sync pomija brudne
worktree (także pliki nieśledzone), konflikty i inne worktree bez wyraźnego wyboru
`--sync-worktrees`. Błąd przerywa wykonanie z niezerowym kodem. Nieznany argument
również kończy skrypt błędem — literówka w `--dry-run` nie uruchomi synchronizacji.

Merge gałęzi poza worktree używa `commit-tree` i `update-ref` ze sprawdzeniem
starego SHA, pomijając hooki i podpisy. Raport ostrzega, jeśli repo ich wymaga.
Brak konfliktów tekstowych nie zastępuje bramki projektu przed pushem.
Audyt zapisuje pliki i tymczasowe obiekty Git; nie zmienia lokalnych gałęzi i nic
nie kasuje. Fetch odświeża refs bez prune. Podgląd sync zapisuje obiekty merge-tree
bez aktualizacji gałęzi.

## Wymagania

Git 2.38+ do synchronizacji, Bash (Windows: Git Bash), Python 3.8+ do raportu,
lokalna sesja klienta z dostępem do repo i powłoki. Bez zależności Pythona.

## Instalacja

Klon zostaje w `C:\dev\claude-skills`. Można zainstalować obie wersje jednocześnie.
Instrukcje używają ścieżki załadowanego skilla; działają również jako kopia albo
w katalogu skilli konkretnego projektu.

Windows — Claude Code:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\git-clean" -Target 'C:\dev\claude-skills\claude\skills\git-clean'
```

Windows — Codex:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills\git-clean" -Target 'C:\dev\claude-skills\codex\skills\git-clean'
```

Repozytoryjna instalacja Codexa: skopiuj paczkę do `.agents/skills/git-clean/`.
[Dokumentacja skilli Codexa](https://learn.chatgpt.com/docs/build-skills).

Linux/macOS, z korzenia klonu:

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/claude/skills/git-clean" ~/.claude/skills/git-clean
ln -s "$PWD/codex/skills/git-clean" ~/.agents/skills/git-clean
```

Zamiast dowiązania można skopiować cały katalog skilla. Przy kopii aktualizacja
wymaga ponownego skopiowania. Przy dowiązaniu wystarcza `git pull`.

**Migracja starej instalacji:** `git-clean/` w korzeniu zostało zastąpione przez
`claude/skills/git-clean/`. Stare dowiązanie trzeba utworzyć ponownie do nowej
ścieżki. Usuwaj samo dowiązanie, nie jego cel; kopia wymaga innego postępowania.
Jeśli klient nie widzi skilla po aktualizacji, rozpocznij nową sesję.

## Użycie

Claude: `/git-clean`. Codex: `$git-clean`. Można też poprosić o audyt gałęzi/stashy.

| Argument | Działanie |
|---|---|
| --no-fetch | dane remote z ostatniego fetcha |
| --stale-days N | próg porzuconej gałęzi; domyślnie 90 |
| --remote-limit N | limit pełnej detekcji squash/rebase remote; domyślnie 100 |
| --graph-limit N | zakres grafu: domyślnie 120, maksymalnie 1000 |
| --no-sync | pomija sync; raport musi dostać --sync none |
| --sync-worktrees | obejmuje inne worktree, po wyraźnym wyborze |

Test bez klienta, z katalogu sprawdzanego repo:

```powershell
& 'C:\dev\claude-skills\codex\skills\git-clean\run.ps1' audit --no-fetch
& 'C:\dev\claude-skills\codex\skills\git-clean\run.ps1' sync --dry-run
& 'C:\dev\claude-skills\codex\skills\git-clean\run.ps1' report --sync dryrun --shell powershell --open
```

Wyniki: `<git-common-dir>/git-clean/` — audit.txt, sync-dryrun.txt, sync-apply.txt,
report.html i history/*.json. W zwykłym repo to `.git/git-clean/`; w worktree
raport leży we wspólnym katalogu Git.

## Rozwój

Zmieniaj skrypty w `shared/git-clean/`, instrukcje w katalogu konkretnego klienta.

```bash
python tools/build_skills.py
python tools/build_skills.py --check
python -m unittest discover -s tests -v
```

`.gitattributes` wymusza LF dla Bash/Pythona i CRLF dla PowerShella. Launcher ma
BOM dla UTF-8 w Windows PowerShell 5.1. Testy tworzą własne repozytoria i nie
sprzątają repo użytkownika.


## Domyślny koszt modelu

- Claude Code: `model: haiku` i `effort: low` w frontmatterze skilla. Model
  sesji wraca po zakończeniu wywołania zgodnie z mechanizmem Claude Code.
- Codex: wykonawca `gpt-6-luna`, reasoning `low`. Entrypoint `$git-clean`
  zleca workflow jednemu subagentowi z jawnym wyborem modelu i minimalnym
  kontekstem. Nadrzędny agent prezentuje wynik i przekazuje decyzje użytkownika.

Codex nie ma udokumentowanego pola `model` we frontmatterze `SKILL.md`.
Dlatego w paczce jest także `launch_codex.py`, który uruchamia interaktywną
sesję CLI na Lunie, bez zmiany globalnego modelu i bez obchodzenia zgód/sandboxa:

```powershell
python 'C:\dev\claude-skills\codex\skills\git-clean\launch_codex.py' --repo 'C:\dev\wybrane-repo' -- --no-fetch
```

Podgląd argumentów bez uruchamiania ani opłaty za model:

```powershell
python 'C:\dev\claude-skills\codex\skills\git-clean\launch_codex.py' --repo 'C:\dev\wybrane-repo' --dry-run -- --no-fetch
```

Sam import skilla nie przełącza modelu nadrzędnego chatu Codexa. Wymagane jest
narzędzie delegowania z wyborem modelu albo launcher CLI. Brak Luny nie oznacza
zgody na droższy model: wykonanie ma się zatrzymać. Jawny wybór użytkownika
może zmienić model. Skrypty liczą klasyfikację i budują graf bez używania LLM.

Wybór Luny sprawdzono 2026-10-06 w
[dokumentacji modeli OpenAI](https://learn.chatgpt.com/docs/model-selection) i
[cenniku Codexa](https://learn.chatgpt.com/docs/pricing).
Wybór modelu subagenta:
[dokumentacja OpenAI](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Frontmatter Claude:
[dokumentacja Claude Code](https://code.claude.com/docs/en/skills).
