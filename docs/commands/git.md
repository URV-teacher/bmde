
## bmde git

Entrypoint: git

Wraps a git client alongside with the VPN needed to connect to the git server and a bypass for the SSH password
    authentication. Currently, the git module also features two opinionated modes to use the git environment: clone mode
    and json mode, which wrap the git command with specific arguments to clone a repository by using its name or the 
    JSON delivery information, instead of supplying the whole git clone ... call. 


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
