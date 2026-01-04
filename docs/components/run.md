# Run Component

The `run` command executes NDS binaries using an emulator (DeSmuME).

## Usage

```bash
bmde run [OPTIONS]
```

## Options

*   `-f`, `--file PATH`: Path to the `.nds` file to run.
*   `-d`, `--directory PATH`: Directory to search for `.nds` files.
*   `--image PATH`: Path to a FAT image to mount.
*   `-e`, `--environment [docker|host|flathub]`: Backend to use.
*   `--debug`: Enable GDB stub on port 1000.
