# Builds the Docker images of the BMDE from this repository (after downloading the assets of each component with its
# scripts/download_assets.sh): the base image (base/), the image of each component (from the checkouts of the
# submodules in components/) and the full development environment (shell/). Each image is built on the images being
# built instead of the published ones, so a change in the base or in a component is tested in all the images that use
# it.
#
#   docker buildx bake                  # every image
#   docker buildx bake full --load      # the full development environment (and the images it needs)
#   docker buildx bake desmume --load   # one component
#   docker buildx bake --push           # build and publish every image

variable "REGISTRY" {
  default = "aleixmt"
}

variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["base", "components", "full"]
}

group "components" {
  targets = ["devkitarm", "desmume", "insight", "dlditool", "grit", "git", "vpn", "vscode"]
}

target "base" {
  context = "base"
  tags    = ["${REGISTRY}/bmde-base:${TAG}"]
}

# The Dockerfiles name the published images they use as stages (e.g. FROM aleixmt/bmde-base:latest AS bmde-base), so
# bake can replace those stages by the targets being built
BASE_IMAGE = {
  bmde-base = "target:base"
}

target "devkitarm" {
  context  = "components/devkitarm-nds-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/bmde-linux:${TAG}"]
}

target "desmume" {
  context  = "components/desmume-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/desmume:${TAG}"]
}

target "insight" {
  context  = "components/insight-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/insight:${TAG}"]
}

target "dlditool" {
  context  = "components/dlditool-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/dlditool:${TAG}"]
}

target "grit" {
  context  = "components/grit-docker"
  contexts = BASE_IMAGE
  tags     = ["${REGISTRY}/grit:${TAG}"]
}

target "git" {
  context    = "components/git-urv-vpn-docker"
  dockerfile = "git.Dockerfile"
  contexts   = BASE_IMAGE
  tags       = ["${REGISTRY}/git-sshpass:${TAG}"]
}

target "vpn" {
  context    = "components/git-urv-vpn-docker"
  dockerfile = "vpn.Dockerfile"
  contexts   = BASE_IMAGE
  tags       = ["${REGISTRY}/forticlient:${TAG}"]
}

target "vscode" {
  context = "components/vscode-arm-syntax-docker"
  # The install script of the extension and its release (src/ and assets/), from its checkout
  contexts = merge(BASE_IMAGE, {
    extension = "components/arm-syntax-vscode-extension"
  })
  tags = ["${REGISTRY}/vscode:${TAG}"]
}

target "full" {
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
  tags = ["${REGISTRY}/bmde-full:${TAG}"]
}
