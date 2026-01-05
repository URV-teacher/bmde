# Architecture

BMDE is built with a modular architecture.

*   **CLI Layer:** Uses `typer` to define commands and arguments.
*   **Service Layer:** Orchestrates the logic for each command.
*   **Backend Layer:** Abstracts the execution environment (Docker, Host).
*   **Configuration:** Uses `pydantic` for settings validation.


BMDE is a CLI tool developed with different abstractions layers. Each layer is in charge of a certain operation or 
abstraction.
The first abstractions are the CLI files, which are the entrypoints of the programs and are in charge of defining which
data accepts each subcommand. Data that accepts each command is classified in three categories:
- The first category are arguments. Arguments are mandatory and represent the data that the command acts upon. 
  Arguments can be detected because it does not make sense to include them in default values for the predefined settings.
  Arguments are present only in the signature of the command functions and not present in the settings. Arguments are 
  also present in the CLI functions and spec. 
- The second category are behavioural parameters. These are arguments that define a behaviour of the program and are not 
  really the data that the program acts upon. Behavioural arguments are present only in the settings, and not present 
  directly in the signature of the command functions, instead, they are wrapped in a settings object. 
- Finally, we have arguments that make sense to be included in settings, for example the NDS FAT image, which is 
  actually an argument, but it makes sense to define a default FAT image. These arguments are included both in the 
  signature of the functions and in the settings object, and in the moment of building the spec, an override of the 
  command arguments against the settings object happen. 