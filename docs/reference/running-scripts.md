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
