## bmde config
Interactively configures `bmde` and writes the answers to a `bmde.toml` file.

`bmde config` goes through every option of the configuration, showing its description, its allowed values and its
current value (the one that results from merging every configuration source) between brackets. Press enter to keep
the current value, type a new one to change it or type `unset` to remove an optional value.

Only the options that change are written, so the rest keep being inherited from the other configuration sources.

### Optional arguments
With a section, e.g. `bmde config run` or `bmde config git.vpn`, only the options of that command or section are
asked. Without it, every command is asked in turn, and you can skip the ones you do not want to configure.

With `-f PATH/TO/bmde.toml` or `--file PATH/TO/bmde.toml` the configuration is written to that file. If omitted, you
are asked whether to write the configuration of the repository (closest `bmde.toml` upward in the tree up to the root
of the git repository, or a new `bmde.toml` in that root) or the configuration of your user (`~/.config/bmde/bmde.toml`
on Linux).

With `-a` or `--advanced` the advanced options (entrypoint, arguments, background, dry run...) are also asked.

### Where each value comes from
`bmde config --show-sources` lists every configuration source from lowest to highest priority (system file, user file,
project file, `BMDE_*` environment variables, the `--config` file and the command line), says which ones were found,
and prints the value of each option with the source that supplied it. Secret values are masked. With a section, e.g.
`bmde config run --show-sources`, only the options of that section are printed.

### Configuration template
`bmde --show-default-config` prints a documented `bmde.toml` with every option and its default value, which can be
used as a template. The file [`examples/bmde.toml`](https://github.com/URV-teacher/bmde/blob/master/examples/bmde.toml)
is regenerated with it on every `make fmt`.
