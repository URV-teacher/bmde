<!-- Improved compatibility of back to top link: See: https://github.com/URV-teacher/bmde/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Unlicense License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Testing PyTest)][pytest-shield]][pytest-url]
[![Style (Ruff)][ruff-shield]][ruff-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/URV-teacher/bmde">
    <img src="https://raw.githubusercontent.com/URV-teacher/hosting/master/assets/logo.webp" alt="Logo">
  </a>

  <h3 align="center">Bare Metal Development Environment (BMDE) CLI</h3>

  <p align="center">
    CLI wrapping the Bare Metal Development Environment (BMDE)
    <br />
    <!-- <a href="https://github.com/URV-teacher/bmde"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/URV-teacher/bmde">View Demo</a> 
    &middot;-->
    <a href="https://github.com/URV-teacher/bmde/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/URV-teacher/bmde/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li>
          <a href="#general-features">General features</a>
          <ul>
            <li><a href="#naive-components">Naive components</a></li>
            <li><a href="#one-module-wraps-one-software">One module wraps one software</a></li>
            <li><a href="#flexibility-using-backend-docker-vs-host-or-others">Flexibility using backend</a></li>
            <li><a href="#config-and-arguments">Config and arguments</a></li>
            <li><a href="#built-with">Built With</a></li>
          </ul>
        </li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#use">Use</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li>
      <a href="#components">Components</a>
      <ul>
        <li>
          <a href="#bmde-run">bmde run</a>
          <ul>
            <li><a href="#mandatory-arguments">Mandatory arguments</a></li>
            <li><a href="#optional-arguments">Optional arguments</a></li>
          </ul>
        </li>
        <li>
          <a href="#bmde-build">bmde build</a>
          <ul>
             <li><a href="#mandatory-arguments-1">Mandatory arguments</a></li>
             <li><a href="#optional-arguments-1">Optional arguments</a></li>
          </ul>
        </li>
        <li>
          <a href="#bmde-patch">bmde patch</a>
          <ul>
             <li><a href="#mandatory-arguments-2">Mandatory arguments</a></li>
             <li><a href="#optional-arguments-2">Optional arguments</a></li>
          </ul>
        </li>
        <li>
          <a href="#bmde-git">bmde git</a>
          <ul>
             <li><a href="#mandatory-arguments-3">Mandatory arguments</a></li>
             <li><a href="#optional-arguments-3">Optional arguments</a></li>
          </ul>
        </li>
        <li>
          <a href="#bmde-edit">bmde edit</a>
          <ul>
             <li><a href="#mandatory-arguments-4">Mandatory arguments</a></li>
             <li><a href="#optional-arguments-4">Optional arguments</a></li>
          </ul>
        </li>
        <li><a href="#bmde-debug">bmde debug</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]]

Operating system agnostic CLI wrapping the Bare Metal Development Environment (BMDE) and other related utilities 
to manage the complete software life-cycle of a NDS C and / or assembly project using 
either host or Dockerized installations of the software components of the BMDE, plus opinionated features to be used in 
the development of the practical exercises from the subject Computers, Operating Systems Structure and in minor cases 
Computer Fundamentals from the university degree of Computer Engineering in the University Rovira i Virgili (URV).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## General features
### Naive components
Each component is independent and can be used individually without using bmde. 

### One module wraps one software
Each module corresponds to a wrapper around one software and its environment.

### Flexibility using backend: Docker vs host (or others)
Each module can be executed using as entrypoint the corresponding binary in your machine (host) or a binary provided by 
Docker embedded in bmde. This allows using bmde but either using a Docker installation that is already provided, or your
own host installations. You can do this for each module (WIP).

In the same sense, some additional backends may be provided, for example, the run command which wraps desmume, also 
provides the FlatHub (`flathub`) backend. 

### Config and arguments
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

Default arguments can be customized via (from less to more priority) 
system variables, global configuration file, specific configuration file of the 
repo, specific
configuration args for the execution.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

This section lists any major languages/frameworks/libraries/tools used in this project. 

* [![Python][Python]][python-url]
* [![Docker][Docker]][Docker-url]
* [![Pydantic][Pydantic]][Pydantic-url]
* [![Typer][Typer]][Typer-url]
* [![FortiClient][FortiClient]][FortiClient-url]
* [![SSH][SSH]][SSH-url]
* [![Expect][Expect]][Expect-url]
* [![Git][Git]][Git-url]
* [![Make][Make]][Make-url]

* [![devkitPro][devkitPro]][devkitPro-url]
* [![devkitARM][devkitARM]][devkitPro-url]
* [![ARM Insight][ARM-Insight]][ARM-url]
* [![GDB][GDB]][GDB-url]

* [![DeSmuME][DeSmuME]][DeSmuME-url]
* [![dlditool][dlditool]][dlditool-url]
* [![X11][X11]][X11-url]
* [![x11vnc][x11vnc]][x11vnc-url]
* [![Flathub][Flathub]][flathub-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
#### Operating system
This CLI has been developed in Ubuntu Linux 20.04.6 LTS (Focal Fossa), so that is the recommended operating system and
version to use. The CLI should work in other Linux systems with minor to none changes to the installation process.

#### Root permissions
You will need root permissions either to do installations or using the bundled Docker components. Usually these 
permissions are acquired using the `sudo` command. 

#### Python
To run the CLI you will need Python installed in your system.

In Debian-like systems you can install it with:
```shell
sudo apt install -y python
```

The recommended version to use for Python is 3.11.  

#### `make`
You can optionally install `make` to automate some of the common operation for the development of the project, such as 
the creation of the virtual environment.

In Debian-like systems you can install it with:
```shell
sudo apt install -y make
```

#### Manual-installed components or `docker` 
You will also need the components of the CLI installed. In this case you can either install them into your system 
manually and 
select `host` as your backend when using the CLI to use those installations, or you can use the Docker containers that 
come bundled with
the CLI by selecting `docker` as your backend when using the CLI.

You can also mix and match `docker`-installed components with `host`-installed components, so there is no need to 
install all components of the same type. Exceptionally, `flathub` is another possible backend to use, but only for the 
run command. 

##### `flathub`
Follow the [oficial installation guide][flathub-setup-url].

In Ubuntu, you can do:
```shell
sudo apt install flatpak
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

##### `docker`
Docker components are easier to use because they do not need an installation and are recommended backend to use for all 
components.

You should install Docker by following the [official Docker installation guide][docker-installation-guide].

In Ubuntu, you can install the latest version of Docker using `apt` with the following:
```shell
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Currently, the CLI calls `docker` directly, so you either need to:
* Run the app as root by calling `sudo`
* Run the app as root by being a privileged user, for example `root`.
* Add your user to the Docker group.

It is recommended to add your user to the `docker` group, so that you do not need to log in as another user or add
`sudo` in front of your call to BMDE each time. 

To add yourself to the Docker group you can use this command:
```shell
sudo usermod -aG docker $USER
```

You need to reboot or log out / log in for these changes to take effect.

##### Manual installed components
You can also install and use the components of the BMDE manually and use them in the CLI.

###### devkitARM
This is the most complex component to install manually, but it can be done. 

You will need to download [`libnds`][libnds-bin] 
and [`devkitARMv46`][devkitarm-bin], 
decompress them in a folder of your machine and create 
environment variables that point to your installation.

The variables are the following:
```
DEVKITPRO=/folder/of/devkitPro \
DEVKITARM=/folder/of/devkitARM \
PATH=/folder/of/devkitARM/bin \
```

A script for the installation of this component will be bundled in the CLI in future versions.

###### `dlditool`
You will need to install `dlditool` only if you want to mount FAT images to your NDS ROMs.

You can download it from [here][dlditool-bin].

You may need a patch file for your ROMs. We have found that MPCF is the only one that works in desmume. You can download
the MPCF patch from [here][dlditool-patch].


###### Rest of manual installed components

In Debian-like systems you can install the rest of the components in a single command with:
```shell
sudo apt install -y git openfortivpn forticlient desmume make ssh
```


### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Clone the repo
    ```shell
    git clone https://github.com/URV-teacher/bmde
    ```
2. Enter the directory
    ```shell
    cd bmde
    ```
3. Install package
    ```shell
    make install
    ```
4. Call the CLI help to check that it has been installed properly
    ```shell
    ./venv/bin/bmde --help
    ```

### Use
You can start using BMDE by cloning a NDS project:
```shell
bmde git clone 12345678-A@git.deim.urv.cat:comp_20
```

Then, enter the directory of the repository you just cloned:
```shell
cd comp_20
```

And build the project with:
```shell
bmde build
```

If the building is successful you will be able to run the project with:
```shell
bmde run
```

You can check out the "Usage" section to see the rest of options available for each component.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Wrap and improve the usage of the software components from BMDE, either from a Docker container or installed in the 
  host. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Components

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

### Mandatory arguments
A valid NDS binary file must be provided for the module to run. This information can be supplied or assumed in different
ways.

With no arguments, this module runs the first `.nds` file found in the directory where `bmde` is invoked. If 
there are more than one `.nds` file in that directory, shows a warning regarding the assumption made.

With `-f PATH/TO/NDS/file.nds` the NDS file to run can be provided with no assumptions. 

With `-d PATH/TO/DIR/WITH/NDS/FILES` the module will behave the same as with no arguments, but using the passed 
directory for finding the `.nds` files.

`-d` and `-f` can not be used together.

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


## bmde debug 
WIP

Debugs a `.nds` file using GDB from terminal or from Insight, possibly using the run backend. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ROADMAP -->
## Roadmap
- [x] Arm syntax workflow auto-publish into VS Code market 
- [ ] Repo VS Code custom, dockerfile VS Code 
- [ ] edit command
- [ ] debug command
- [x] additional controls of desmume (needs compilation)
- [x] icon of tot inside the devkitarm
- [ ] configuration defaults from bmde from desmume
- [x] awesome readme with logo
- [ ] dev / test dependencies
- [ ] mount logs
- [ ] Explore linting tools black and ruff and automate them
- [x] Reestructure CLI.py in a folder with a file for each command

See the [open issues][issues-url] for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the free software community such an amazing place to learn, inspire, and create. Any 
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also 
simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Top contributors:

<a href="https://github.com/URV-teacher/bmde/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=URV-teacher/bmde" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Proudly distributed with love under the GNU GPLv3 License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

[@AleixMT][aleixmt-github-profile] - aleix.marine@urv.cat

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

The teachers of URV who have collaborated.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/URV-teacher/bmde.svg?style=for-the-badge
[contributors-url]: https://github.com/URV-teacher/bmde/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/URV-teacher/bmde.svg?style=for-the-badge
[forks-url]: https://github.com/URV-teacher/bmde/network/members
[stars-shield]: https://img.shields.io/github/stars/URV-teacher/bmde.svg?style=for-the-badge
[stars-url]: https://github.com/URV-teacher/bmde/stargazers
[issues-shield]: https://img.shields.io/github/issues/URV-teacher/bmde.svg?style=for-the-badge
[issues-url]: https://github.com/URV-teacher/bmde/issues
[license-shield]: https://img.shields.io/github/license/URV-teacher/bmde.svg?style=for-the-badge
[license-url]: https://github.com/URV-teacher/bmde/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/aleixmt
[pytest-shield]: https://github.com/URV-teacher/bmde/actions/workflows/test.yml/badge.svg
[pytest-url]: https://github.com/URV-teacher/bmde/actions/workflows/test.yml
[ruff-shield]: https://github.com/URV-teacher/bmde/actions/workflows/lint.yml/badge.svg
[ruff-url]: https://github.com/URV-teacher/bmde/actions/workflows/lint.yml
[product-screenshot]: https://raw.githubusercontent.com/URV-teacher/hosting/master/assets/screenshot.png

[flathub-setup-url]: https://flathub.org/en/setup
[Flathub]: https://img.shields.io/badge/Flathub-%234a90d9.svg?style=for-the-badge&logo=flathub&logoColor=white
[flathub-url]: https://flathub.org/apps/details/YOUR_APP_ID
[dlditool-bin]: https://www.chishm.com/DLDI/downloads/dlditool-linux-x86_64.zip
[dlditool-patch]: https://www.chishm.com/DLDI/downloads/mpcf.dldi
[libnds-bin]: https://raw.githubusercontent.com/URV-teacher/devkitarm-nds-docker/master/data/libnds.tar.bz2
[docker-installation-guide]: https://docs.docker.com/engine/install/ubuntu/
[devkitarm-bin]: https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2
[aleixmt-github-profile]: https://github.com/AleixMT

[Python]: https://img.shields.io/badge/Python-%230db7ed.svg?style=for-the-badge&logo=python&logoColor=blue
[python-url]: https://www.python.org/

[Docker]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/

[Pydantic]: https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white
[Pydantic-url]: https://docs.pydantic.dev/

[Typer]: https://img.shields.io/badge/Typer-000000?style=for-the-badge&logo=python&logoColor=white
[Typer-url]: https://typer.tiangolo.com/

[FortiClient]: https://img.shields.io/badge/FortiClient-C01818?style=for-the-badge&logo=fortinet&logoColor=white
[FortiClient-url]: https://www.fortinet.com/support/product-downloads

[SSH]: https://img.shields.io/badge/SSH-232F3E?style=for-the-badge&logo=ssh&logoColor=white
[SSH-url]: https://www.openssh.com/

[Expect]: https://img.shields.io/badge/Expect-1a1b26?style=for-the-badge&logo=tcl&logoColor=white
[Expect-url]: https://core.tcl-lang.org/expect/index

[Git]: https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white
[Git-url]: https://git-scm.com/

[Make]: https://img.shields.io/badge/Make-A42E2B?style=for-the-badge&logo=gnu&logoColor=white
[Make-url]: https://www.gnu.org/software/make/

[devkitPro]: https://img.shields.io/badge/devkitPro-E65100?style=for-the-badge
[devkitPro-url]: https://devkitpro.org/

[devkitARM]: https://img.shields.io/badge/devkitARM-E65100?style=for-the-badge
[devkitARM-url]: https://devkitpro.org/wiki/Getting_Started

[ARM-Insight]: https://img.shields.io/badge/ARM_Insight-0091BD?style=for-the-badge&logo=arm&logoColor=white
[ARM-url]: https://www.arm.com/

[GDB]: https://img.shields.io/badge/GDB-A42E2B?style=for-the-badge&logo=gnu&logoColor=white
[GDB-url]: https://www.sourceware.org/gdb/

[DeSmuME]: https://img.shields.io/badge/DeSmuME-4B6C22?style=for-the-badge
[DeSmuME-url]: http://desmume.org/

[dlditool]: https://img.shields.io/badge/DLDI_Tool-808080?style=for-the-badge
[dlditool-url]: https://www.chishm.com/DLDI/

[X11]: https://img.shields.io/badge/X11-EF5350?style=for-the-badge&logo=xorg&logoColor=white
[X11-url]: https://www.x.org/

[x11vnc]: https://img.shields.io/badge/x11vnc-EF5350?style=for-the-badge
[x11vnc-url]: https://github.com/LibVNC/x11vnc

