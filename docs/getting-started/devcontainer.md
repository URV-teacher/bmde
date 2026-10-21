# Dev container

Instead of installing the BMDE in your computer, you can develop your NDS projects inside the full development
environment of the BMDE (`aleixmt/bmde-full`) from VS Code, with a
[dev container](https://code.visualstudio.com/docs/devcontainers/containers). Everything is ready inside: devkitARM
and libnds, DeSmuME, Insight, dlditool, grit, git and the VPN of the URV. VS Code runs its terminal, extensions and
debugger inside the container, and your project stays in your computer.

## Requirements

* [Docker](https://docs.docker.com/get-docker/): Docker Engine in Linux, Docker Desktop in Windows and macOS.
* [VS Code](https://code.visualstudio.com/) with the
  [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
* In Windows, [WSL 2](https://learn.microsoft.com/windows/wsl/install): keep your project inside WSL (e.g.
  `~/projects/...`) and open it from there, with Docker Desktop using the WSL 2 backend.

## Usage

1. Copy the folder
   [`.devcontainer/nds/`](https://github.com/URV-teacher/bmde/tree/master/.devcontainer/nds) of the BMDE repository to
   the root of your project as `.devcontainer/`, so you have `.devcontainer/devcontainer.json`.
2. Open the project in VS Code and run **Dev Containers: Reopen in Container** from the command palette (`F1`). The
   first time it downloads the image (about 3 GB).
3. Use the terminal of VS Code as usual: `make`, `desmume game.nds`, `insight`, `git`...

## Graphical programs

DeSmuME and Insight open their windows in the X server of your computer (X11), which is what the template does:

| Your computer | X11 (default) | VNC |
| --- | --- | --- |
| Linux (X11, or Wayland with Xwayland) | ✅ | ✅ |
| Windows 11 with the project in WSL 2 (WSLg) | ✅ | ✅ |
| macOS | ❌ | ✅ |
| GitHub Codespaces | ❌ (the container does not start) | ✅ |

When X11 is not available, switch to VNC: in `.devcontainer/devcontainer.json`, delete or comment out `containerEnv`,
`mounts` and `initializeCommand`, uncomment the VNC block below them and rebuild the container (**Dev Containers:
Rebuild Container**). The windows are then shown in a virtual screen: open it with a VNC viewer (e.g.
[TigerVNC](https://tigervnc.org/) or [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)) connected
to `localhost:5900`. There is no sound in the container.

## VPN

To reach the git server of the course from outside the URV, the container can connect to the VPN of the URV, which
needs the `--cap-add=NET_ADMIN --device=/dev/ppp` of `runArgs`. If your Docker has no `/dev/ppp` and the container does
not start, remove that line (you will not be able to use the VPN from the container).

## Without VS Code

[`shell/compose.yml`](https://github.com/URV-teacher/bmde/blob/master/shell/compose.yml) runs the same image from a
terminal, on the project of the current directory, with everything the components need: the windows and the sound of
your computer, the VPN, and the settings of DeSmuME and VS Code kept between runs:

```shell
cd ~/nds/my-project
docker compose -f /path/to/bmde/shell/compose.yml run --rm bmde        # a shell: make, desmume, insight, git...
docker compose -f /path/to/bmde/shell/compose.yml run --rm bmde make   # or a single command
```

For the VPN and the git server, write your credentials in `shell/.env` (`VPN_USERNAME`, `VPN_PASSWORD`, `SSH_USERNAME`,
... listed at the top of the file); git ignores it, never commit it. On a computer without an X server (e.g. macOS),
switch to VNC as explained in the comments of the file. `BMDE_TAG=1.14.0` pins a version of the image.

## Version

The template uses `aleixmt/bmde-full:latest`, so rebuilding the container (**Dev Containers: Rebuild Container**)
updates it to the latest BMDE. Each release of the BMDE is also published as `X.Y.Z`, `X.Y` and `X` (e.g.
`aleixmt/bmde-full:1.14`), to keep a fixed version.
