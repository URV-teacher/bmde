

## bmde edit
This module edits NDS projects using different backends as IDEs / editors.

### Mandatory arguments
A valid directory must be provided for the module to run. This information can be supplied or assumed in 
different
ways.

With no arguments, this module executes an IDE in the directory where `bmde` is invoked. 

With `-d PATH/TO/DIR/WITH/NDS/PROJECT` the module will behave the same as with no arguments, but using the passed 
directory as the directory where the NDS project to build is located.

### Optional arguments
With `-e` or `--environment docker|(host|bmde)` you can choose what backend you are using to build the NDS 
binary. 
* With `docker`
it uses the `vscode-docker` project to edit the project.
* With `host` uses the shell command `vscode` to edit the project, whatever is the implementation of the underlying 
binary.

The default entrypoint for all backends is `vscode`.

The option 
`--entrypoint PATH/TO/ENTRYPOINT` is available, which allows to override the file executed as entrypoint.

All options after `--` will be passed to the underlying entrypoint if possible.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.   

