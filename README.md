# bmde
Operating system agnostic CLI wrapping the Bare Metal Development Environment (BMDE) and other related utlities 
to manage the complete software life cycle of a NDS C and / or assembly project using 
either host installations or Dockerized installations, plus opinionated features to be used in 
the development of the practical exercises from the subject Computers, Operating Systems Structure and in minor cases 
Computer Fundamentals from the university degree of Computer Engineering in the University Rovira i Virgili.

# Usage cases
Wrap and improve the usage of the software components from BMDE, either from a Docker container or installed in the 
  host. 

# General features
## Naive components
Each component is independent and can be used individually without using bmde. 

## One module wraps one software
Each module corresponds to a wrapper around one software and its environment.

## Flexibility using backend: Docker vs host (or others)
Each module can be executed using as entrypoint the corresponding binary in your machine (host) or a binary provided by 
Docker embedded in bmde. This allows using bmde but either using a Docker installation that is already provided, or your
own host installations. You can do this for each module (WIP).

In the same sense, some additional backends may be provided, for example, the run command which wraps desmume, also 
provides the flathub backend. 

## Config and arguments
A native toml schema is included to provide default values to arguments to bmde. bmde also reads configuration from various
sources with different priority, allowing for fine-grained control over each repository. The priority is the following, 
with later mentioned sources overriding previous:
* Environment variables.
* `/etc/bmde/bmde.toml`
* `~/.config/bmde/bmde.toml`
* Closest `bmde.toml` upward in the tree
* Explicit configuration via arguments pointing to a valid .toml file.

The configuration files allows an easy usage to bmde: Provided arguments via config files can be omitted from the 
arguments of the CLI call to bmde, allowing shorter commands and skipping the need to provide things like credentials 
for authentication in each call to bmde. 


# BMDE components wrapped
## git
Entrypoint: git

Wraps a git client alongside with the VPN needed to connect to the git server and a bypass for the SSH password
    authentication. Currently, the git module also features two opinionated modes to use the git environment: clone mode
    and json mode, which wrap the git command with specific arguments to clone a repository by using its name or the 
    JSON delivery information, instead of supplying the whole git clone ... call. 

## build
Entrypoint: make

Wraps the whole devkitARM from devkitPro environment (make, arm-none-eabi, ndstool and other utilities) for 
    building the .NDS binaries from source. 

## run
Entrypoint: desmume

Wraps desmume and desmume-cli alongside a VNC server and / or X11 client (Docker mode only), which allows the 
    desmume screen to be seen from a VNC client () or as a native window if using X11 (Linux).  Features automatic killing of the 
    entrypoint process in case the main of the NDS rom reached its end or the exit function is called, which is useful 
    for automated behaviour. 

## patch
Entrypoint: dlditool

Patches NDS rom to be used with MPCF FAT driver, in order to allow the NDS rom to write in a FAT disk image.

## debug (WIP)
Debugs a `.nds` file using GDB from terminal or from Insight, possibly using the run backend. 


## Components

## CLI modules
### bmde run
This module runs NDS binaries using different backends. 

(If possible, depending on the backend) this module features the exit of the runner process if the main function of the 
binary reached its end, which is useful 
when testing NDS software.

#### Mandatory arguments
A valid NDS binary file must be provided for the module to run. This information can be supplied or assumed in different
ways.

With no arguments, this module runs the first `.nds` file found in the directory where `bmde` is invoked. If 
there are more than one `.nds` file in that directory, shows a warning regarding the assumption made.

With `-f PATH/TO/NDS/file.nds` the NDS file to run can be provided with no assumptions. 

With `-d PATH/TO/DIR/WITH/NDS/FILES` the module will behave the same as with no arguments, but using the passed 
directory for finding the `.nds` files.

`-d` and `-f` can not be used together.

#### Optional arguments
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


## bmde build
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
it uses the devkitarm-docker project to run the binary. 
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

## bmde patch
This module patches NDS binaries so that they can access a FAT image.

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
it uses the devkitarm-docker project to run the binary. 
* With `host` uses the shell command `desmume` to run the binary, whatever is the implementation of the underlying 
binary.

The default backend is `docker`.

If possible, the option `--dry-run` will be implemented to simulate what the program would do.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.   


## bmde git
This module wraps a custom pre-configured `git` environment.

This module features the possibility of being able to connect to a `forticlient` VPN inside the container, which is 
useful when connecting to `git` servers behind this type of VPN. It also features a bypass of the authentication prompt
from the `git` server using provided credentials, making the `git` process to execute non-interactive. 

### Mandatory arguments
Some of the mandatory arguments contain sensible data, they can only be provided 
via file or system variable. 

The file must have a key-value format (as in `.env` files). A file can be provided with the argument `-p` 
`--password-file 
PATH/TO/PASSWORD/FILE`. The file `.env` of the directory where `bmde` is executed is always used.

The same keys that can be provided in the file, can be used with underscores and capital letters for providing the 
arguments via system variables. 

The priority to read the different values from more to less priority is: via `-p` argument, via `.env` file in the 
execution directory and system variables. The meaning, values and syntax for each argument in its possible sources are 
explained 
below.

You will need to provide the VPN details if you want the VPN on. The required VPN details are the following:
% TODO: complete details, defaults and structure with table
* VPN username | VPN_USERNAME | vpn-username
* VPN password  
* VPN host
* VPN port

You can provide the `git` user details to author the commits you make in the repository. The required `git` details are 
the 
following:
* git name
* git email

You will need to provide the `git` user credentials to be able to connect to the server. The required `git` credentials
are:
* git username
* git password
* git host


### Optional arguments
A valid `git` project directory could be provided to the module to run `git` commands inside it. This information can be 
supplied, or it will be assumed.

With no arguments, this module assumes as project directory the directory where `bmde` is invoked. 

With `-d PATH/TO/DIR/WITH/NDS/FILES` the module will behave the same as with no arguments, but using the passed 
directory as the directory where the NDS project to build is located.

With `-e` or `--environment docker|(host|bmde)` you can choose what backend you are using to build the NDS 
binary. 
* With `docker`
it uses the `fortivpn-git-docker` project to run the binary. 
* With `host` uses the shell command `git` to run the binary, whatever is the implementation of the underlying 
binary.

The default entrypoint for all backends is `git`.

When using the backend `docker`, the option `-s` or `--shell` can be used, which gives a shell inside
the Docker container with the `git` environment.

All options after `--` will be passed to the underlying entrypoint.

If possible, the option `--dry-run` will be implemented to simulate what the program would do.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.   

With `--vpn on|off` you can control the VPN. The default is `on`.


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
it uses the vscode-docker project to edit the project.
* With `host` uses the shell command `vscode` to edit the project, whatever is the implementation of the underlying 
binary.

The default entrypoint for all backends is `vscode`.

The option 
`--entrypoint PATH/TO/ENTRYPOINT` is available, which allows to override the file executed as entrypoint.

All options after `--` will be passed to the underlying entrypoint if possible.

With `--verbose` shows more information and with `--trace` shows all logs. With `-q` shows no output.   

## bmde patch
For patching a NDS file with dlditool


## Argument and configuration behaviour
Default arguments can be customized via (from less to more priority) 
system variables, global configuration file, specific configuration file of the 
repo, specific
configuration args for the execution.

# WIP
Arm syntax workflow autopublish into vscode market 
Repo vscode custom, dockerfile vscode 
edit command
debug command
additional controls of desmume (needs compilation)


# Acknowledgements