
## bmde build
Entrypoint: make

Wraps the whole devkitARM from devkitPro environment (make, `arm-none-eabi`, `ndstool` and other utilities) for
    building the .NDS binaries from source.

This module compiles NDS projects using different backends as building environments.

### Mandatory arguments
A valid NDS project directory must be provided for the module to run. This information can be supplied or assumed in
different
ways.

With no arguments, this module executes `make` in the directory where `bmde` is invoked.

With `-d PATH/TO/DIR/WITH/NDS/FILES` the module will behave the same as with no arguments, but using the passed
directory as the directory where the NDS project to build is located.

### Optional arguments
With `-e` or `--environment docker|(host|bmde)` you can choose what backend you are using to build the NDS
binary.
* With `docker`
it uses the `devkitarm-docker` project to run the binary.
* With `host` uses the shell command `desmume` to run the binary, whatever is the implementation of the underlying
binary.

The default entrypoint for all backends is `make`.

The option
`--entrypoint PATH/TO/ENTRYPOINT` is available, which allows to override the file executed as entrypoint.

When using the backend `docker`, the option `-s` or `--shell` can be used, which gives a shell inside
the Docker container
used for building the project.

All options after `--` will be passed to the underlying entrypoint if possible.

If possible, the option `--dry-run` will be implemented to simulate what the program would do.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.

### Icon of the ROM
The icon of the `.nds` in the menu of the console (and of flash cards and emulators) is the file of the variable
`GAME_ICON` of the Makefile, which `ndstool` puts into the banner of the ROM. The Makefile of the course sets it to the
icon of libnds, `$(DEVKITPRO)/libnds/icon.bmp` (also the default of the `ds_rules` of devkitARM), which in the
`aleixmt/devkitarm-nds` image is `/URV/bmde/devkitPro/libnds/icon.bmp`.

Use `--icon PATH/TO/icon.bmp` (or `icon = "PATH/TO/icon.bmp"` under `[build]` in the config, relative to the project
directory) to use another icon. It must be a 32x32 BMP with a palette (indexed colours, like the default one, which
has 8 bits per pixel) using at most 16 colours; the first colour of the palette is transparent. The ROM does not depend
on the icon in the Makefile of the course, so run `bmde build clean` first if the ROM is already built.

* With the `docker` backend, the icon is mounted read-only over the default icon of the image. It is used by every
  Makefile that uses the default icon, also from another `--entrypoint` (e.g. `/bin/bash`), but not by a Makefile that
  sets `GAME_ICON` to another file (e.g. an `icon.bmp` of the project).
* With the `host` backend, the libnds of the host is not modified: `GAME_ICON=PATH/TO/icon.bmp` is passed to `make`,
  which overrides the `GAME_ICON` of any Makefile. It is ignored with another `--entrypoint`.

To do the same without `bmde`, mount the icon over the default one when running the image:

```shell
docker run --rm -v "$PWD:/input/project" -w /input/project \
  -v "$PWD/icon.bmp:/URV/bmde/devkitPro/libnds/icon.bmp:ro" aleixmt/devkitarm-nds
```

or add it to the `volumes` of the service that builds the project in a `compose.yml`:

```yaml
    volumes:
      - .:/input/project
      - ./icon.bmp:/URV/bmde/devkitPro/libnds/icon.bmp:ro
```
