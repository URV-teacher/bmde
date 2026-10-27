# Builds the Docker images of the BMDE from this repository (after downloading the assets of each component with its
# scripts/download_assets.sh): the base image (base/), the image of each component (from the checkouts of the
# submodules in components/), the full development environment (shell/), the development environment of the bmde
# CLI (.devcontainer/bmde-dev/) and the bmde CLI in Docker (Dockerfile). Each image is built on the images being
# built instead of the published ones, so a change in the base or in a component is tested in all the images that use
# it.
#
#   docker buildx bake --list=targets   # what can be built (--list=variables for the variables)
#   docker buildx bake                  # every image
#   docker buildx bake full --load      # the full development environment (and the images it needs)
#   docker buildx bake desmume --load   # one component
#   docker buildx bake --push           # build and publish every image
#   VERSION=1.14.0 docker buildx bake --push   # also tag the published images 1.14.0, 1.14 and 1

variable "REGISTRY" {
  description = "Docker Hub namespace of the images"
  default     = "aleixmt"
}

variable "TAG" {
  description = "Tag of every image (CI pushes the tested images as sha-<commit>)"
  default     = "latest"
}

# Version of the bmde release the images belong to (X.Y.Z, without the v). When set, every image is also tagged X.Y.Z,
# X.Y and X, besides TAG. The CLI of a release runs the images tagged with its version, so students get the
# environment it was tested with (and can pin another one with docker.image_tag in bmde.toml)
variable "VERSION" {
  description = "bmde release (X.Y.Z) to also tag every image with: X.Y.Z, X.Y and X"
  default     = ""
}

# Layer cache: empty (no cache besides the one of the local builder) or "gha", which CI sets so each run only rebuilds
# what changed instead of everything (devkitARM, DeSmuME and Insight are compiled from their sources). Every target
# has its own scope, because targets writing to the same scope would overwrite the cache of each other. mode=max also
# exports the layers of the build stages (e.g. the one compiling Insight), which are not in the final image
variable "CACHE" {
  description = "Layer cache to read and write, one scope per target: empty (none) or gha (GitHub Actions)"
  default     = ""
}

function "cache_from" {
  params = [name]
  result = CACHE == "" ? [] : ["type=${CACHE},scope=${name}"]
}

# A failed export (e.g. the cache service is down or full) must not fail a build that succeeded
function "cache_to" {
  params = [name]
  result = CACHE == "" ? [] : ["type=${CACHE},scope=${name},mode=max,ignore-error=true"]
}

function "tags" {
  params = [image]
  result = concat(
    ["${REGISTRY}/${image}:${TAG}"],
    VERSION == "" ? [] : [
      "${REGISTRY}/${image}:${VERSION}",
      "${REGISTRY}/${image}:${join(".", slice(split(".", VERSION), 0, 2))}",
      "${REGISTRY}/${image}:${split(".", VERSION)[0]}",
    ]
  )
}

group "default" {
  description = "Every image"
  targets     = ["base", "components", "full", "dev", "cli"]
}

group "components" {
  description = "The image of each component, from the submodules in components/"
  targets     = ["devkitarm", "desmume", "insight", "dlditool", "grit", "git", "vpn", "vscode"]
}

target "base" {
  description = "aleixmt/bmde-base: the Ubuntu image, with the users and helpers of the BMDE, of every other image"
  context     = "base"
  tags        = tags("bmde-base")
  cache-from  = cache_from("base")
  cache-to    = cache_to("base")
}

# The Dockerfiles name the published images they use as stages (e.g. FROM aleixmt/bmde-base:latest AS bmde-base), so
# bake can replace those stages by the targets being built
BASE_IMAGE = {
  bmde-base = "target:base"
}

target "devkitarm" {
  description = "aleixmt/devkitarm-nds: devkitARM r46 and libnds, to build NDS programs (bmde build)"
  context     = "components/devkitarm-nds-docker"
  contexts    = BASE_IMAGE
  tags        = tags("devkitarm-nds")
  cache-from  = cache_from("devkitarm")
  cache-to    = cache_to("devkitarm")
}

target "desmume" {
  description = "aleixmt/desmume: the DeSmuME 0.9.11 emulator, to run NDS programs (bmde run)"
  context     = "components/desmume-docker"
  contexts    = BASE_IMAGE
  tags        = tags("desmume")
  cache-from  = cache_from("desmume")
  cache-to    = cache_to("desmume")
}

target "insight" {
  description = "aleixmt/insight: Insight 7.3.50 and gdb-multiarch, to debug NDS programs (bmde debug)"
  context     = "components/insight-docker"
  contexts    = BASE_IMAGE
  tags        = tags("insight")
  cache-from  = cache_from("insight")
  cache-to    = cache_to("insight")
}

target "dlditool" {
  description = "aleixmt/dlditool: dlditool, to patch a DLDI driver into NDS programs (bmde patch)"
  context     = "components/dlditool-docker"
  contexts    = BASE_IMAGE
  tags        = tags("dlditool")
  cache-from  = cache_from("dlditool")
  cache-to    = cache_to("dlditool")
}

target "grit" {
  description = "aleixmt/grit: grit, to convert images into graphics data for NDS programs"
  context     = "components/grit-docker"
  contexts    = BASE_IMAGE
  tags        = tags("grit")
  cache-from  = cache_from("grit")
  cache-to    = cache_to("grit")
}

target "git" {
  description = "aleixmt/git-sshpass: git and sshpass, for the git server of the course (bmde git)"
  context     = "components/git-urv-vpn-docker"
  dockerfile  = "git.Dockerfile"
  contexts    = BASE_IMAGE
  tags        = tags("git-sshpass")
  cache-from  = cache_from("git")
  cache-to    = cache_to("git")
}

target "vpn" {
  description = "aleixmt/forticlient: the FortiClient VPN, to reach the network of URV (bmde git)"
  context     = "components/git-urv-vpn-docker"
  dockerfile  = "vpn.Dockerfile"
  contexts    = BASE_IMAGE
  tags        = tags("forticlient")
  cache-from  = cache_from("vpn")
  cache-to    = cache_to("vpn")
}

target "vscode" {
  description = "aleixmt/vscode: Visual Studio Code with the ARM assembly syntax extension of the course"
  context     = "components/vscode-arm-syntax-docker"
  # The install script of the extension and its release (src/ and assets/), from its checkout
  contexts = merge(BASE_IMAGE, {
    extension = "components/arm-syntax-vscode-extension"
  })
  tags       = tags("vscode")
  cache-from = cache_from("vscode")
  cache-to   = cache_to("vscode")
}

target "full" {
  description = "aleixmt/bmde-full: the full development environment, with the tools of every component"
  context     = "shell"
  contexts = merge(BASE_IMAGE, {
    components = "components"
    devkitarm  = "target:devkitarm"
    desmume    = "target:desmume"
    insight    = "target:insight"
    dlditool   = "target:dlditool"
    grit       = "target:grit"
    vscode     = "target:vscode"
  })
  tags       = tags("bmde-full")
  cache-from = cache_from("full")
  cache-to   = cache_to("full")
}

target "dev" {
  description = "aleixmt/bmde-dev: the full development environment plus what developing the bmde CLI needs"
  context     = ".devcontainer/bmde-dev"
  contexts = {
    bmde-full = "target:full"
  }
  tags       = tags("bmde-dev")
  cache-from = cache_from("dev")
  cache-to   = cache_to("dev")
}


target "cli" {
  description = "aleixmt/bmde: the bmde CLI in Docker, on the development environment of the CLI"
  context     = "."
  contexts = {
    bmde-dev = "target:dev"
  }
  # The CLI of a release runs the images tagged with its version (without VERSION, a development version: the latest)
  args = VERSION == "" ? {} : {
    BMDE_VERSION = VERSION
  }
  tags       = tags("bmde")
  cache-from = cache_from("cli")
  cache-to   = cache_to("cli")
}
