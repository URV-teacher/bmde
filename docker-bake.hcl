# Builds the Docker images of the BMDE from this repository (after downloading the assets of each component with its
# scripts/download_assets.sh): the base image (base/), the image of each component (from the checkouts of the
# submodules in components/), the full development environment (shell/) and the development environment of the bmde
# CLI (.devcontainer/bmde-dev/). Each image is built on the images being
# built instead of the published ones, so a change in the base or in a component is tested in all the images that use
# it.
#
#   docker buildx bake                  # every image
#   docker buildx bake full --load      # the full development environment (and the images it needs)
#   docker buildx bake desmume --load   # one component
#   docker buildx bake --push           # build and publish every image
#   VERSION=1.14.0 docker buildx bake --push base full dev   # also tag the published images 1.14.0, 1.14 and 1

variable "REGISTRY" {
  default = "aleixmt"
}

variable "TAG" {
  default = "latest"
}

# Version of the bmde release the images belong to (X.Y.Z, without the v). When set, the images published by this
# repository (base, full and dev) are also tagged X.Y.Z, X.Y and X, besides TAG
variable "VERSION" {
  default = ""
}

# Layer cache: empty (no cache besides the one of the local builder) or "gha", which CI sets so each run only rebuilds
# what changed instead of everything (devkitARM, DeSmuME and Insight are compiled from their sources). Every target
# has its own scope, because targets writing to the same scope would overwrite the cache of each other. mode=max also
# exports the layers of the build stages (e.g. the one compiling Insight), which are not in the final image
variable "CACHE" {
  default = ""
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
  targets = ["base", "components", "full", "dev"]
}

group "components" {
  targets = ["devkitarm", "desmume", "insight", "dlditool", "grit", "git", "vpn", "vscode"]
}

target "base" {
  cache-from = cache_from("base")
  cache-to   = cache_to("base")
  context = "base"
  tags    = tags("bmde-base")
}

# The Dockerfiles name the published images they use as stages (e.g. FROM aleixmt/bmde-base:latest AS bmde-base), so
# bake can replace those stages by the targets being built
BASE_IMAGE = {
  bmde-base = "target:base"
}

target "devkitarm" {
  cache-from = cache_from("devkitarm")
  cache-to   = cache_to("devkitarm")
  context  = "components/devkitarm-nds-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/bmde-linux:${TAG}"]
}

target "desmume" {
  cache-from = cache_from("desmume")
  cache-to   = cache_to("desmume")
  context  = "components/desmume-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/desmume:${TAG}"]
}

target "insight" {
  cache-from = cache_from("insight")
  cache-to   = cache_to("insight")
  context  = "components/insight-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/insight:${TAG}"]
}

target "dlditool" {
  cache-from = cache_from("dlditool")
  cache-to   = cache_to("dlditool")
  context  = "components/dlditool-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/dlditool:${TAG}"]
}

target "grit" {
  cache-from = cache_from("grit")
  cache-to   = cache_to("grit")
  context  = "components/grit-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/grit:${TAG}"]
}

target "git" {
  cache-from = cache_from("git")
  cache-to   = cache_to("git")
  context    = "components/git-urv-vpn-docker"
  dockerfile = "git.Dockerfile"
  contexts   = BASE_IMAGE
  tags       = ["${REGISTRY}/git-sshpass:${TAG}"]
}

target "vpn" {
  cache-from = cache_from("vpn")
  cache-to   = cache_to("vpn")
  context    = "components/git-urv-vpn-docker"
  dockerfile = "vpn.Dockerfile"
  contexts   = BASE_IMAGE
  tags       = ["${REGISTRY}/forticlient:${TAG}"]
}

target "vscode" {
  cache-from = cache_from("vscode")
  cache-to   = cache_to("vscode")
  context = "components/vscode-arm-syntax-docker"
  # The install script of the extension and its release (src/ and assets/), from its checkout
  contexts = merge(BASE_IMAGE, {
    extension = "components/arm-syntax-vscode-extension"
  })
  tags = ["${REGISTRY}/vscode:${TAG}"]
}

target "full" {
  cache-from = cache_from("full")
  cache-to   = cache_to("full")
  context = "shell"
  contexts = merge(BASE_IMAGE, {
    components = "components"
    devkitarm  = "target:devkitarm"
    desmume    = "target:desmume"
    insight    = "target:insight"
    dlditool   = "target:dlditool"
    grit       = "target:grit"
    vscode     = "target:vscode"
  })
  tags = tags("bmde-full")
}

target "dev" {
  cache-from = cache_from("dev")
  cache-to   = cache_to("dev")
  context = ".devcontainer/bmde-dev"
  contexts = {
    bmde-full = "target:full"
  }
  tags = tags("bmde-dev")
}
