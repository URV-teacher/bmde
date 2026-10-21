# shellcheck shell=sh
# Loads the environment (PATH, DEVKITPRO...) of the BMDE programs installed in /URV/bmde, which their install
# scripts write to /etc/profile.d/bmde-*.sh. Login shells read those files themselves; the image loads this file in
# the rest of shells (BASH_ENV and /etc/bash.bashrc) and before the commands run with bmde-exec.
for bmde_env_file in /etc/profile.d/bmde-*.sh; do
  if [ -r "${bmde_env_file}" ]; then
    # shellcheck source=/dev/null
    . "${bmde_env_file}"
  fi
done
unset bmde_env_file
