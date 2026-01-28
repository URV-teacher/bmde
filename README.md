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
[![PyPI][pypi-shield]][pypi-url]
[![Docs][docs-shield]][docs-url]


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
    <a href="https://urv-teacher.github.io/bmde/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <!-- <a href="https://github.com/URV-teacher/bmde">View Demo</a> 
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
      <a href="#roadmap">Roadmap</a>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

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
To run `bmde` you will need Python 3.11 installed in your system.

To run a command you will need either Docker with permissions for the user executing `bmde` `COMMAND` or the 
software that the command wraps directly installed in your system. For simplicity, we recommend sticking to Docker.

[Check out the docs for a full explanation on the prerequisites][docs-prerequisites].



### Installation

Install the command by using:
```shell
pip install bmde
```

You may add an alias to your binary to shorten up the command from `python -m bmde` to `bmde`:
```shell
echo "alias bmde=python -m bmde" >> ~/.bashrc
```

[Check out the docs for a full explanation on the installation][docs-installation].



### Usage
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

[Check out the docs for a full explanation on the usage][docs-usage].

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

See the [project roadmap][roadmap-url] for a full list of proposed features, and known [issues][issues-url] and its 
implementation state).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Check out our [CONTRIBUTING.md][contributing-url] to know how to make a contribution.

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
[pypi-shield]: https://github.com/URV-teacher/bmde/actions/workflows/release.yml/badge.svg
[pypi-url]: https://github.com/URV-teacher/bmde/actions/workflows/release.yml
[docs-url]: https://urv-teacher.github.io/bmde/
[docs-prerequisites]: https://urv-teacher.github.io/bmde/
[docs-installation]: https://urv-teacher.github.io/bmde/
[docs-usage]: https://urv-teacher.github.io/bmde/
[contributing-url]: https://github.com/URV-teacher/bmde/blob/master/CONTRIBUTING.md
[docs-shield]: https://github.com/URV-teacher/bmde/actions/workflows/docs.yml/badge.svg
[docs-url]: https://github.com/URV-teacher/bmde/actions/workflows/docs.yml

[Flathub]: https://img.shields.io/badge/Flathub-%234a90d9.svg?style=for-the-badge&logo=flathub&logoColor=white
[flathub-url]: https://flathub.org/apps/details/YOUR_APP_ID
[aleixmt-github-profile]: https://github.com/AleixMT
[roadmap-url]: https://github.com/orgs/URV-teacher/projects/3

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
