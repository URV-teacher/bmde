#!/bin/bash
# From https://github.com/URV-teacher/computers-practical-corrections/blob/master/src/checkout_repos.sh

set -e

parse_data()
{
  # Parse data
  name="$(cat "$1" | ${JQ} .name | tr -d "\"")"
  email="$(cat "$1" | ${JQ} .email | tr -d "\"")"
  repo="$(cat "$1" | ${JQ} .repo | tr -d "\"")"
  branch="$(cat "$1" | ${JQ} .branch | tr -d "\"")"
  tests="$(cat "$1" | ${JQ} .tests | tr -d "\"")"
  fusion="$(cat "$1" | ${JQ} .fusion | tr -d "\"")"
  lab="$(cat "$1" | ${JQ} .lab | tr -d "\"")"
  blocks="$(cat "$1" | ${JQ} .blocks | tr -d "\"")"
  phase="$(cat "$1" | ${JQ} .phase | tr -d "\"")"
  call="$(cat "$1" | ${JQ} .call | tr -d "\"")"
}


# Description: Corrects the computers practical exercise of one student
# $1 SHA ID of the commit to checkout
checkout_fusion()
{
  # Perform clone and checkout code
  rm -rf "/repos/${phase_text}-${call_text}-${repo}-${branch}-fusion"
  #GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  /git_clone.exp ${DNI} ${GIT_SERVER} ${repo} "/repos/${phase_text}-${call_text}-${repo}-${branch}-fusion" "$PASS"
  {
    # shellcheck disable=SC2164
    cd "/repos/${phase_text}-${call_text}-${repo}-${branch}-fusion"
    git checkout "${fusion}"
  }
}

# Description: Corrects the computers practical exercise of one student
# $1 test number
# SHA_ID to checkout
checkout_test()
{
  # Perform clone and checkout code
  rm -rf "/repos/${phase_text}-${call_text}-${repo}-${branch}-test$1"
  #GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  /git_clone.exp ${DNI} ${GIT_SERVER} ${repo} "/repos/${phase_text}-${call_text}-${repo}-${branch}-test$1" "$PASS"
  {
    # shellcheck disable=SC2164
    cd "/repos/${phase_text}-${call_text}-${repo}-${branch}-test$1"
    git checkout "$2"
  }
}


# $1 phase
# $2 call
main()
{

  echo "
************************************************************************************************************************
* Computers course 2024-2025
* Corrections for practical exercise phase 1
************************************************************************************************************************
"
  for file in "/data/"*.json; do
    if [[ -f "${file}" ]]; then
      parse_data "${file}"

      if [ $phase == 1 ]; then
        phase_text="1stPhase"
      else
        phase_text="2ndPhase"
      fi

      if [ $call == 1 ]; then
        call_text="1stCall"
      else
        call_text="2ndCall"
      fi
        echo "
      ************************************************************************************************************************
      * Student: ${name} (${email})
      * Branch: ${branch}
      ************************************************************************************************************************"

      checkout_fusion
      # Use jq to extract the 'tests' array and loop through it
      i=0
      for test_value in $(jq -r '.tests[]' < "${file}"); do
        i=$((i + 1))
        checkout_test $i "${test_value}"
      done
    fi
  done
}

DNI="$(cat /run/secrets/ssh_username)"
PASS="$(cat /run/secrets/ssh_password)"
GIT_SERVER="$(cat /run/secrets/ssh_host)"
JQ=jq

#git config --global http.postBuffer 524288000  # Set a larger buffer size
#git config --global core.compression 0         # Disable compression


main "$@"