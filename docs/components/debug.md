# Debug Component

The `debug` command launches a debugger (Insight/GDB) connected to the emulator.

## Usage

```bash
bmde debug [OPTIONS]
```

## Options

*   `--nds PATH`: Path to the `.nds` file.
*   `--elf PATH`: Path to the `.elf` file (for symbols).
*   `-e`, `--environment [docker|host]`: Backend to use.
