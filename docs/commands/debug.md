## bmde debug
Entrypoint: debugger (Insight by default) + desmume in debug mode

Debugs an NDS program: it runs the `.nds` ROM in DeSmuME with its GDB stub enabled, as `bmde run --debug` would do, and
in parallel a debugger loaded with the `.elf` of the same program and ready to connect to DeSmuME. It is the equivalent
of `make debug` in the Windows BMDE. When the debugger is closed, DeSmuME is stopped.

```bash
cd MyProject      # Folder of the project, with the .nds and .elf built by bmde build
bmde debug
```

The `.nds` and `.elf` files are searched in the current directory, or can be given with `--nds PATH/TO/file.nds` and
`--elf PATH/TO/file.elf`.

### Debuggers
Choose the debugger with `-g` or `--debugger` (or `debugger = "..."` under `[debug]` in the config):

* `insight` (default): the graphical debugger of the Windows BMDE, built from the same sources (GDB/Insight
  7.3.50.20110803). Press the **Run** button to connect to DeSmuME: the program is downloaded, stops at `main`, and
  can be debugged from there. Unlike in Windows, there is no need to configure the target (Remote/TCP, port) first.
* `gdb-multiarch`: GDB in the terminal, already connected to DeSmuME (stopped at the entry point of the program). Use
  the usual GDB commands, for example `break main`, `continue`, `next`, `print variable` or `bt`.

The output of DeSmuME is written to `bmde-debug-emulator.log` in the temporary directory (usually `/tmp`), so it does
not mix with the debugger.

### Backends
With `-b` or `--backend docker|host` you can choose how the debugger is executed:

* `docker` (default): uses the [insight-docker](https://github.com/URV-teacher/insight-docker) image, which contains
  both debuggers. The project is mounted in the same path used by `bmde build`, so the debugger finds the source code
  of the `.elf`. The preferences, sessions and breakpoints of Insight are kept in the Docker volume
  `insight_docker_config` between runs.
* `host`: uses `arm-eabi-insight` (or `insight`) or `gdb-multiarch` from the `PATH`. Insight is not preconfigured: use
  "Run > Connect to target" with target "Remote/TCP", hostname `localhost` and the debug port.

DeSmuME is run with the backend of `bmde run` configured under `[debug.run]` in the config (`docker` by default), so
its options (sound, controls, FAT image...) also apply to debug sessions.

### Optional arguments
With `-p` or `--port` you can choose the port of the GDB stub of DeSmuME (1024 by default).

With `-s` or `--screen host|vnc|none` you choose how the windows of DeSmuME and of the debugger are shown when they run
in Docker: as windows of the desktop (`host`, the default), through VNC (`vnc`, DeSmuME on port 5900 and the debugger
on 5901 of `localhost`) or not shown (`none`).

When using the backends `host` and `docker`, the option `--entrypoint PATH/TO/ENTRYPOINT` is available, which allows
to override the file executed as entrypoint of the debugger.

All options after `--` will be passed to the debugger.

With `--dry-run` the commands that would be executed are shown, without executing them.
