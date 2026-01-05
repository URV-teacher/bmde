## bmde run
Entrypoint: desmume

Wraps desmume and desmume-cli alongside a VNC server and / or X11 client (Docker mode only), which allows the 
    desmume screen to be seen from a VNC client () or as a native window if using X11 (Linux).  Features automatic killing of the 
    entrypoint process in case the main of the NDS rom reached its end or the exit function is called, which is useful 
    for automated behaviour. 

This module runs NDS binaries using different backends. 

(If possible, depending on the backend) this module features the exit of the runner process if the main function of the 
binary reached its end, which is useful 
when testing NDS software.


### Optional arguments
With `--image PATH/TO/FAT/file.fat` the module will load the FAT image as file into the runner if possible. 

With `-e` or `--environment docker|(host|bmde)|flatpak` you can choose what backend you are using to execute the NDS 
binary. 
* With `docker`
it uses the desmume-docker project to run the binary. Currently, this backend has no screen output, but it could be 
implemented in the future if the host has a VNC-compatible display server. The default entrypoint for this backend is 
`desmume-cli`
* With `host` uses the shell command `desmume` to run the binary, whatever is the implementation of the underlying 
binary. The default entrypoint for this backend is `desmume`.
* With `flatpak` uses the FlatPak implementation of DeSmuME. 

If not specified, the backend will be assumed depending on the presence of each backend in the system. If there are 
more than one possible backend, it will be chosen from the options, from more priority to less priority: `host`, 
`docker` and finally `flathub`.

When using the backends `host` and `docker`, the option 
`--entrypoint PATH/TO/ENTRYPOINT` is available, which allows to override the file executed as entrypoint.

When using the backend `docker`, the option `-s` or `--shell` can be used, which gives a shell inside
the Docker container
used for running the project.

All options after `--` will be passed to the underlying entrypoint if possible.

With `--debug`, the execution of the runner, if possible, starts with GDB stubs on and the runner waits for connection 
on port 1000.

With `-p` or `--port`, you can choose which port to expose for the debugger to connect. This assumes `--debug`.

If possible, the option `--dry-run` will be implemented to simulate what the program would do.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.   
