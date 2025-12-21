"""
Defines the schema of settings of the application
"""
from typing import Optional, List

from pydantic import BaseModel, FilePath

from bmde.core import logging
from bmde.core.logging import LogLevelLiteral
from bmde.core.types import BackendName, RunBackendName, RunDockerOutputName



class LoggingSettings(BaseModel):
    level: LogLevelLiteral = "info"
    file: Optional[FilePath] = None


class RunSettings(BaseModel):
    backend: Optional[RunBackendName] = "docker"
    docker_screen: Optional[RunDockerOutputName] = None
    entrypoint: Optional[str] = "desmume"
    logging: LoggingSettings = None
    passthrough: Optional[List[str]] = None

    debug: bool = False
    port: int = 1000
    image: Optional[str] = None


class BuildSettings(BaseModel):
    backend: Optional[BackendName] = None
    entrypoint: Optional[str] = "make"
    logging: LoggingSettings = None
    passthrough: Optional[List[str]] = None


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
    backend: Optional[BackendName] = "docker"
    entrypoint: Optional[str] = None
    logging: LoggingSettings = "debug"
    passthrough: Optional[List[str]] = None

    git: GitConfigSettings = GitConfigSettings()
    ssh: GitSshSettings = GitSshSettings()
    vpn: VpnAuthSettings = VpnAuthSettings()


class PatchSettings(BaseModel):
    backend: Optional[BackendName] = None
    entrypoint: Optional[str] = None
    logging: LoggingSettings = None
    passthrough: Optional[List[str]] = None


class Settings(BaseModel):
    logging: LoggingSettings = LoggingSettings()
    run: RunSettings = RunSettings()
    build: BuildSettings = BuildSettings()
    git: GitSettings = GitSettings()
    patch: PatchSettings = PatchSettings()
