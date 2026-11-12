# Running a kit script

A kit script is a `.py` file a skill names, next to that skill. Pick the interpreter in this order (1.127.0). Stop at the first one that runs the script.

1. `python3`
2. `python`
3. `py -3` on Windows

A command is not found when the shell says it is missing, and when Windows prints the Store alias message `Python was not found`. Treat that message as not found and try the next interpreter. Do not stop on it.

```text
python3 <skill folder>/scripts/<script>.py
python <skill folder>/scripts/<script>.py
py -3 <skill folder>/scripts/<script>.py
```

Use the same interpreter for every script in that run once one of them works. Do not hand-edit the file the script owns.

## A silent finder (1.136.0)

Copy one of these when the shell should pick the interpreter and stay quiet. Try `python3`, then `python`, then `py -3`. The Windows Store alias writes `Python was not found`. That message means the command was not found. Do not stop on it, and do not print it.

```bash
crav1_python() {
  local candidate out
  for candidate in python3 python "py -3"; do
    out=$(eval "$candidate -c \"import sys\"" 2>&1) || true
    if printf '%s' "$out" | grep -q "Python was not found"; then
      continue
    fi
    if eval "$candidate -c \"import sys\"" >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}
```

```powershell
function Get-Crav1Python {
  foreach ($candidate in @("python3", "python", "py -3")) {
    $parts = $candidate -split " ", 2
    $arg = @("-c", "import sys")
    if ($parts.Length -gt 1) { $arg = @($parts[1]) + $arg }
    $out = & $parts[0] @arg 2>&1 | Out-String
    if ($out -match "Python was not found") { continue }
    if ($LASTEXITCODE -eq 0) { return $candidate }
  }
  return $null
}
```

Do not use `/tmp` as a portable path. On Windows that path is not the temp folder. Use the host temp directory (`$TMPDIR`, `$TEMP`, or `[System.IO.Path]::GetTempPath()`), or write the script's result to stdout and skip a file.

`scripts/build_map.py --recommend T1` needs a spec folder. Passing `tasks.md` or `spec.md` prints `A spec folder is required` and the parent folder to pass instead.
