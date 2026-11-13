# Running a kit script

A kit script is a `.py` file a skill names, next to that skill. Pick the interpreter (1.144.0). Stop at the first one that runs the script.

On Windows the interpreter is `python`. Elsewhere it is `python3`. If that command is missing, try the next one.

1. On Windows: `python`, then `py -3`, then `python3`
2. Elsewhere: `python3`, then `python`, then `py -3`

A command is not found when the shell says it is missing, and when Windows prints the Store alias message `Python was not found`. Treat that message as not found and try the next interpreter. Do not stop on it. Do not run `python3` alone on Windows. That name is often the Store alias.

Set UTF-8 for the process: `PYTHONUTF8=1` and `-X utf8`. Use the same interpreter for every script in that run once one of them works. Do not hand-edit the file the script owns.

```text
# Windows
$env:PYTHONUTF8 = "1"
python -X utf8 <skill folder>/scripts/<script>.py

# Elsewhere
PYTHONUTF8=1 python3 -X utf8 <skill folder>/scripts/<script>.py

# When both of those are missing
py -3 -X utf8 <skill folder>/scripts/<script>.py
```

In a skill instruction, `<interpreter>` means that choice. The command still includes every argument the script requires.

```text
<interpreter> -X utf8 <skill crav1-tasks-ready-to-build>/scripts/resolve_spec.py "<query>" --root docs/specs
```

`resolve_spec.py` reads `docs/specs` when `--root` is omitted and that folder exists. Pass `--root docs/specs` anyway. A missing folder is an error that names that flag.

```text
<interpreter> -X utf8 <skill crav1-tasks-ready-to-build>/scripts/build_map.py docs/specs/<slug> --recommend T1
```

## A silent finder (1.136.0)

Copy one of these when the shell should pick the interpreter and stay quiet. On Windows try `python`, then `py -3`, then `python3`. Elsewhere try `python3`, then `python`, then `py -3`. The Windows Store alias writes `Python was not found`. That message means the command was not found. Do not stop on it, and do not print it. The finder sets `PYTHONUTF8=1`. Pass `-X utf8` when you run the script.

```bash
crav1_python() {
  local candidate out
  local -a candidates
  candidates=(python3 python "py -3")
  case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*|CYGWIN*) candidates=(python "py -3" python3) ;;
  esac
  if [ "${OS:-}" = "Windows_NT" ]; then
    candidates=(python "py -3" python3)
  fi
  for candidate in "${candidates[@]}"; do
    out=$(eval "$candidate -c \"import sys\"" 2>&1) || true
    if printf '%s' "$out" | grep -q "Python was not found"; then
      continue
    fi
    if eval "$candidate -c \"import sys\"" >/dev/null 2>&1; then
      export PYTHONUTF8=1
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}
```

```powershell
function Get-Crav1Python {
  $candidates = @("python3", "python", "py -3")
  if ($env:OS -eq "Windows_NT") { $candidates = @("python", "py -3", "python3") }
  foreach ($candidate in $candidates) {
    $parts = $candidate -split " ", 2
    $arg = @("-c", "import sys")
    if ($parts.Length -gt 1) { $arg = @($parts[1]) + $arg }
    $out = & $parts[0] @arg 2>&1 | Out-String
    if ($out -match "Python was not found") { continue }
    if ($LASTEXITCODE -eq 0) { $env:PYTHONUTF8 = "1"; return $candidate }
  }
  return $null
}
```

Do not use `/tmp` as a portable path. On Windows that path is not the temp folder. Use the host temp directory (`$TMPDIR`, `$TEMP`, or `[System.IO.Path]::GetTempPath()`), or write the script's result to stdout and skip a file.

`<interpreter> -X utf8 <skill>/scripts/build_map.py docs/specs/<slug> --recommend T1` needs that spec folder. Passing `tasks.md` or `spec.md` prints `A spec folder is required` and the parent folder to pass instead. The first line is the branch name (1.140.0). Later lines are `source`, `from`, and `because`. Do not use those later lines as the branch name.
