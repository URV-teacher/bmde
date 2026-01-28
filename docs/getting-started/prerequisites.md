
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

[flathub-setup-url]: https://flathub.org/en/setup
[docker-installation-guide]: https://docs.docker.com/engine/install/ubuntu/
[libnds-bin]: https://raw.githubusercontent.com/URV-teacher/devkitarm-nds-docker/master/data/libnds.tar.bz2
[dlditool-bin]: https://www.chishm.com/DLDI/downloads/dlditool-linux-x86_64.zip
[dlditool-patch]: https://www.chishm.com/DLDI/downloads/mpcf.dldi
[devkitarm-bin]: https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/devkitARM_r46-x86_64-linux.tar.bz2
