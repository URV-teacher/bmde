Partial port of the BMDE (bare metal development environment) to Linux (and subsequently to Docker) from the URV 
subject 
Computer Fundamentals, 
Computers and Operating System Structure, to achieve compilation of the C and assembly projects of the subjects into
runnable `.nds` roms.

The original BMDE is an environment to compile, run, debug and develop NDS (Nintendo DS) software projects written in C 
and ARM Assembly for Windows systems in a didactic manner. 

This BMDE only contains the tools and documentation to compile NDS software projects inside a Docker container or Linux.
This is useful to be able
to compile NDS homebrew project without setting up the environment, because the whole environment is already set up 
inside the Docker container.

![NDS homebrew icon](data/libnds/icon.bmp)

# Components
## Libraries provided by devkitPro 
From the original BMDE environment. Originally obtained from devkitPro updater v1.6.0 for Windows (AFAIK lost media 
currently).

| Library     | Version  |
|-------------|----------|
| libgba      | 0.5.0    |
| libgbafat   | 1.1.0    |
| maxmodgba   | 1.0.10   |
| libnds      | 1.6.2    |
| libndsfat   | 1.1.0    |
| defaultarm7 | 0.7.1    |
| filesystem  | 0.9.13-1 |
| dswifi      | 0.4.0    |
| libmirko    | 0.9.7    |
| maxmodds    | 1.0.10   |
| libctru     | 1.2.1    |
| citro3d     | 1.2.0    |


## devkitARM
Version 46, downloaded from [here](https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/).

# Removed components from original BMDE
| Name         | Version         | Notes                                                             |
|--------------|-----------------|-------------------------------------------------------------------|
| msys         | 1.0.17-1        | Not needed since we already have a working Linux environment      |
| 3dsexamples  | 20170226        | Not needed for compilation, can be included afterwards            |
| ndsexamples  | 20170124        | Not needed for compilation, can be included afterwards            |
| gbaexamples  | 20170228        | Not needed for compilation, can be included afterwards            |
| gp32examples | 20051021        | Not needed for compilation, can be included afterwards            |
| insight      | 7.3.50.20110803 | Not needed, we do not want to debug the software, only compile it |

# Usage
## Requirements to build and run projects via Docker
* Docker (one of the latest version that includes the plugin `docker compose`)
* Source code for homebrew project for the NDS that uses `make`/`Makefile` for compilation.

## Compile a NDS project that has a makefile
### Manually
###### Download `docker-compose.yml`
Inside the root of your homebrew project (in the same folder as a `Makefile`) download
[this `docker-compose.yml`](https://raw.githubusercontent.com/URV-teacher/bmde-linux/master/examples/compose.yml).

###### Run container
Afterward, use `docker compose up` to run the container, which will compile the software. 
You can use Docker Desktop to run the `compose.yml`.

###### Clean containers and volumes
You can clean the used images, containers and volumes using Docker Desktop. 


### From terminal
You can also do these steps from the terminal:
```shell
cd my-project
wget https://raw.githubusercontent.com/URV-teacher/bmde-linux/master/examples/compose.yml  # Download compose.yml
docker compose up  # Run container 
docker system prune -af  # Clean images and containers
docker volume prune -af  # Clean volumes
```

### Final result
After the execution you should see the resulting compilation files where your `Makefile` instructs them to be. Usually
these places are `build/` for the temporary objects and the root folder of the project for the final binary files,
usually the files `input.elf` and `input.nds` for normal homebrew projects and `.dldi` for dldi patch projects.

### How to change the name for the binary files
Usually Makefiles are instructed with creating the final binary files with the same name as the name of the folder they
are in. Since in the `compose.yml` we provide the project is mounted into `/input` the final binaries will have that
name (`input.nds`, `input.elf` or `input.dldi`).

If you want binaries to have the name of the folder they are in, you usually must modify the volume mounting point and 
the compilation entrypoint by adding the name of your project folder.
```dockerfile
    volumes:
      - ./:/input/project-name
    entrypoint: sh -c "cd /input/project-name && make clean && make"
```


## Run a shell inside the BMDE environment for Linux
You can also run the BMDE environment with your homebrew project inside if you want to inspect anything from inside the
container image
or want to do the compilation process of your software manually.
```shell
docker compose run --entrypoint /bin/bash bmde-linux
# Type commands you want in a shell inside the container
```


## Customizing / extending the BMDE environment container
Inside your project folder, create a `Dockerfile` with a `FROM` directive that points to the Docker container of
`bmde-linux`:
```dockerfile
# Extend bmde-linux container
FROM aleixmt/bmde-linux:latest
# Add any more instruction for the building of your image, you way want to COPY .
# COPY . /input  # You may want to add COPY directives to copy files from your project to the container image
```

All the added files with a `COPY` directive will be inside the image, so if you add confidential or secret files do
not push the image to the docker registry.


## Customizing / extending the BMDE environment container entrypoint
You can use a custom `entrypoint.sh` file to customize the behaviour of the container when it starts. We provide an
`entrypoint.sh` file for starters that does the same as the entrypoint we provide in the example `compose.yml` file.

To configure the `compose.yml` file to use your `entrypoint.sh` as entrypoint, you need to comment the entrypoint
directive from the `compose.yml` file:
```yaml
    #entrypoint: sh -c "cd /input && make clean && make"
```

You also need to copy `entrypoint.sh` to the same folder as your `Dockerfile` and `compose.yml`.

Finally, you need to have these in the end of your `Dockerfile` to copy the entrypoint inside the container and set it 
to be used:
```dockerfile
# Uncomment to use custom entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

You can do this to change the commands used to compile the software by using your `entrypoint.sh` to do so. 
Modifications done by you entrypoint to the container are not conserved into the image, so the entrypoint can include 
confidential information and upload the image afterward safely. 

## Run container as your user to avoid conflicting permissions
The container is run as root, which means that the files created by it will be owned by this user. This means that we 
need to change the permissions of the files if we want to delete or move them. 

To avoid having to do this change of permissions every time we do the compilation, we can add an `user` directive in our 
`compose.yml` file to make the container run as ourselves, and we can control the files directly.

To implement this behaviour, we will run the commands `id -u` and `id -g` to find out our UID and GID values. 
Usually, these values are 1000 and 1000.
These values will be passed to the container using the user directive like this:
```dockerfile
    user: 1000:1000
```

After this, just run `docker compose up` and the files created by the container will be owned by you. 


## Use environment for manual usage inside container through `docker run`
With docker installed, use:
```shell
docker run -it aleixmt/bmde-linux:latest
```

Since we are running the image directly without loading any data inside it, we will enter inside the container in
interactive mode.

To put data inside it, we will probably need to install some commands to connect to the Internet. For example, to
install git:
```shell
apt-get install -y git
```

Afterwards, we can clone a repo, for example, we could do:
```shell
git clone https://github.com/URV-teacher/hello-world-nds
```

And then `cd` inside the repository and compile the software with `make`.

To move the results of the compilation (usually `.nds` files),
you can communicate a folder from inside the container with a folder of your host by adding parameters into the `docker
run` command to mount a volume. I will not explain it because it is better to use the `compose.yml` through `docker
compose`, which automatically mounts volumes.


## Install it directly into your Linux system for manual usage
This is not the preferred way to run this software, but is possible to do it, though I am (currently) not providing
scripts to automatically do so. I will provide some instructions if someone wants to try it out, since surprisingly with
the right binaries the environment works with minor changes.

1. Download devkitARM from [here](https://wii.leseratte10.de/devkitPro/devkitARM/r46%20%282017%29/) and decompress it.
2. Decompress `libnds.tar.bz2` from the `data` folder of this repository.
3. Mount the following tree from any file system point of your like, but this will condition the subsequent steps:
```
/ANY_FOLDER/
/ANY_FOLDER/devkitPro/
/ANY_FOLDER/devkitPro/devkitARM
/ANY_FOLDER/devkitPro/libnds
```
Also, create the environment variables `DEVKITPRO=/ANY_FOLDER/devkitPro`, `DEVKITARM=$DEVKITPRO/devkitARM` and
`DESMUME="/"`. This last variable has a "dummy" definition because it is needed for compatibility purposes. Also add the
path `$DEVKITARM/bin` into the beginning of the `PATH` environment variable.

You can do it with:
```shell
PATH=$DEVKITARM/bin:$PATH
```
4. Move the decompressed files of devkitARM into `/ANY_FOLDER/devkitPro/devkitARM` and the decompressed files of
   `libnds.tar.bz2` into
   `/ANY_FOLDER/devkitPro/libnds`
5. Install `make` using your package manager `sudo apt install -y make` and use `make` to try to compile your software.
6. If the `#include <nds.h>` directive does not found the corresponding file, add the `include` folder from the `libnds`
   into the `base_rules` of devkitPro: `$(CC) -I/ANY_FOLDER/devkitPro/libnds/include/ -c myfile.c`
7. Afterwards, if it still does not work, you will need to add the binaries of the libnds library manually into
   `ds_rules` for linking `.o` to `.elf`. The error after step 6 looked like this:
```
/bmde/devkitPro/devkitARM/bin/../lib/gcc/arm-none-eabi/6.3.0/../../../../arm-none-eabi/bin/ld: cannot find -lnds9
```
You need to add `-L/path/to/libnds` to the corresponding `Makefile` rule (the one that is failing).
8. Finally, the `ndstool` will be complaining about not finding the `default.elf`, which to solve I move to the
   location were `ndstool` was expecting the file. I could not change the "rule" files like I did in previous steps 
   because
   I could not find a way to configure `ndstool` to use the `default.elf` file from another location.
9. Finally, you can open a terminal in the project that you want to compile and execute `make` to compile the project.
   The projects can be located in any path of your liking.

Installation steps may change, specially the ones regarding the specification of paths of libraries in the base rules of
the devkitARM toolchain. Luckily, when building the container, we do not needed to specify the path of any libraries.
They were found automatically.

## Run `.nds` files into DeSmuME
At this moment, I recommend using `flatpak` to run DeSmuME:
```shell
flatpak install flathub org.desmume.DeSmuME
flatpak run org.desmume.DeSmuME
```

This will run DeSmuME in a containerized manner, using another container technology for graphical applications called
`flatpak`.

# Developer usage
Clone the repository, enter the project folder and run an IDE to run in the project.
```shell
git clone https://github.com/URV-teacher/bmde-linux
cd bmde-linux
pycharm .
```

## Building
To build the Docker image.
```shell
cd bmde-linux
docker container rm bmde-linux  # To remove the container if already exists
BUILDKIT_PROGRESS=plain docker build --rm bmde -t aleixmt/bmde-linux:latest . 
```

## Push image to dockerhub
To push it to Dockerhub (needs authentication first).
```shell
docker push aleixmt/bmde-linux:latest
```

## Run and force rebuild of image 
To make a "clean" run of the image, because we force the rebuild of the base image. 
```shell
cd bmde-linux
docker container rm bmde-linux  # To remove the container if already exists
BUILDKIT_PROGRESS=plain docker compose up --build --rm bmde-linux
```

## Test with real example
You can test the environment using the [`hello-world-nds`](https://github.com/URV-teacher/hello-world-nds) project, 
which is a very simple homebrew project that prints hello world in the NDS screen. 
```shell
git clone https://github.com/URV-teacher/hello-world-nds
cd hello-world-nds
wget https://raw.githubusercontent.com/URV-teacher/bmde-linux/master/examples/compose.yml  # Once per makefile
docker compose up  # With the working directory of the shell in the same folder as Makefile and compose.yml
```

## Run tests
We want to make sure that the binaries generated are exactly equal to the binaries generated
with the original BMDE (or at least functionally equal). To do so, we got the NDS examples of devkitPro, compiled them
with the original BMDE environment and the BMDE linux port, hashed the resulting files with a SHA1 checksum and checked 
for equality.

The results are the following:
```
bmde-linux-test-1  | Test failed for 256_color_bmp/win_build/256_color_bmp.nds 8c85fdc4e3c56e812c358dda222ea9c733641005 different than 256_color_bmp/256_color_bmp.nds 18d459992646baffa26396eb71025f172ad2215e
bmde-linux-test-1  | Test failed for Display_List/win_build/Display_List.nds 3f2e8145a270b02a5b26ba2d0c0694e922044fd0 different than Display_List/Display_List.nds 9dd03041e53200b9ebb183b0239f07b6bd503fad
bmde-linux-test-1  | Test failed for Display_List_2/win_build/Display_List_2.nds 476858e06d353b4d7c51a1669310653f4b2c135b different than Display_List_2/Display_List_2.nds 27bd63d6b8254adbbaf78458b3ce6e39507c45af
bmde-linux-test-1  | Test failed for Env_Mapping/win_build/Env_Mapping.nds f0aa9b6cdb7456b15a0f79ca2e8d9246332f8891 different than Env_Mapping/Env_Mapping.nds 540f85029bb49de3d06c9a54b822a56bc0549ddf
bmde-linux-test-1  | Test failed for Picking/win_build/Picking.nds b8ed0e9f41b670f88731fde2d94218b99862823b different than Picking/Picking.nds a4c62651dc008c9f0dc904b469a4fd20f677b6e4
bmde-linux-test-1  | Test failed for Toon_Shading/win_build/Toon_Shading.nds badd96db180299680955bc52609043f80ba4fc0e different than Toon_Shading/Toon_Shading.nds 1a6f0f622f2aba3766df685fe48bb17fb0c89457
bmde-linux-test-1  | Test failed for all_in_one/win_build/all_in_one.nds 595de1cc99b4709db6a06c1c16b001b8cb3292e4 different than all_in_one/all_in_one.nds 943b3d45af4f078d87245f562b08015f859f8d50
bmde-linux-test-1  | Test failed for backgrounds/win_build/backgrounds.nds 5ef537a489be5f93edf37c10e8fece3968b7a91e different than backgrounds/backgrounds.nds 4eb04b66d80fbb58065c3a234284a6d5b8469d08
bmde-linux-test-1  | Test failed for rotation/win_build/rotation.nds f53794e9369e65a236ffa45759ff20f3b0d95574 different than rotation/rotation.nds 9106c5f5e0b682f8e9b9c6b45f29307984272aff
bmde-linux-test-1  | Test failed for windows/win_build/windows.nds 9874bcc7b20b93b206b0afa8d4a2d4081fcf5263 different than windows/windows.nds ec813391a241ffa8c90ded34a98392b0e4864331
bmde-linux-test-1  | Test failed for arm9lib/win_build/libarm9lib.a c28f729e521b55193052832973b4b31985969b8e different than arm9lib/lib/libarm9lib.a c2b2b948d152066d85458ac2f23fcbd5b7deab8d
bmde-linux-test-1  | 65 out of 76 tests passed.
```

You can reproduce these results by yourself by using
```shell
cd bmde-linux/test
docker compose up --build
```


# Acknowledgements
