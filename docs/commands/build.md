
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
