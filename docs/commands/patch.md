

## bmde patch
Entrypoint: dlditool

Patches NDS rom to be used with Media Player Compact Flash (MPCF) FAT driver, in order to allow the NDS rom to write in a FAT disk image.

This module patches NDS binaries so that they can access a FAT image.

For patching a NDS file with dlditool.

### Mandatory arguments
A valid NDS binary must be provided for the module to run. This information can be supplied or assumed in 
different
ways.

With no arguments, this module patches the first `.nds` file found in the directory where `bmde` is invoked. 

With `-f PATH/TO/DIR/WITH/NDS/file.nds` the module will behave the same as with no arguments, but using the passed 
file as the file to be patched. 

### Optional arguments
With `-e` or `--environment docker|(host|bmde)` you can choose what backend you are using to build the NDS 
binary. 
* With `docker`
it uses the `devkitarm-docker` project to run the binary. 
* With `host` uses the shell command `desmume` to run the binary, whatever is the implementation of the underlying 
binary.

The default backend is `docker`.

If possible, the option `--dry-run` will be implemented to simulate what the program would do.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.   

