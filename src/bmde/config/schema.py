"""
Defines the schema of settings of the application
"""

from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, FilePath

from bmde.core.logging import LogLevel
from bmde.core.types import BackendOptions, RunBackendOptions, DockerOutputOptions


class LoggingSettings(BaseModel):
    level: LogLevel = LogLevel("info")
    file: Optional[FilePath] = None


class RunSettings(BaseModel):
    backend: Optional[RunBackendOptions] = None
    docker_screen: Optional[DockerOutputOptions] = None
    entrypoint: Optional[Path] = Path("desmume")
    arguments: Optional[List[str]] = None

    debug: bool = False
    port: int = 1000
    image: Optional[str] = None


class BuildSettings(BaseModel):
    backend: Optional[BackendOptions] = None
    entrypoint: Optional[Path] = None
    arguments: Optional[List[str]] = None


class VpnAuthSettings(BaseModel):
    enabled: bool = True
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    cert: Optional[str] = None
    realm: Optional[str] = None
    test_dns: Optional[str] = None
    test_ip: Optional[str] = None


class GitSshSettings(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None


class GitConfigSettings(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class GitSettings(BaseModel):
    backend: Optional[BackendOptions] = BackendOptions("docker")
    entrypoint: Optional[Path] = None
    arguments: Optional[List[str]] = None

    git: GitConfigSettings = GitConfigSettings()
    ssh: GitSshSettings = GitSshSettings()
    vpn: VpnAuthSettings = VpnAuthSettings()


class PatchSettings(BaseModel):
    backend: Optional[BackendOptions] = None
    entrypoint: Optional[Path] = None
    arguments: Optional[List[str]] = None


class DebugSettings(BaseModel):
    run: RunSettings = RunSettings()

    backend: Optional[BackendOptions] = None
    docker_screen: Optional[DockerOutputOptions] = None
    entrypoint: Optional[Path] = Path("insight")
    arguments: Optional[List[str]] = None


class Settings(BaseModel):
    logging: LoggingSettings = LoggingSettings()
    run: RunSettings = RunSettings()
    build: BuildSettings = BuildSettings()
    git: GitSettings = GitSettings()
    patch: PatchSettings = PatchSettings()
    debug: DebugSettings = DebugSettings()
