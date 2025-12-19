#!/bin/bash

test_checksums()
{
    win="$(sha1sum "$1" | cut -f1 -d " " )"
    nix="$(sha1sum "$2" | cut -f1 -d " " )"
    if [ "${win}" == "${nix}" ]; then
      TESTS_PASSED=$(( TESTS_PASSED + 1))
    else
      msg="${NEWLINE}Test failed for $1 ${win} different than $2 ${nix}"
      SUMMARY+="${msg}"
      OUTPUT_MSG+="${msg}${NEWLINE}${NEWLINE}Failed with message:${NEWLINE}${comp_msg}"
    fi
    TOTAL_TESTS=$(( TOTAL_TESTS + 1))
}

TOTAL_TESTS=0
TESTS_PASSED=0
OUTPUT_MSG=""
NEWLINE=$'\n'
SUMMARY=""

cd test/roms
for i in *; do
  if [ "$i" == "Makefile" ]; then
    continue
  fi
  comp_msg=$(cd "$i" && make clean && make 2>&1)
  test_checksums "$i/win_build/$i.nds" "$i/$i.nds"
done

cd ../libs
comp_msg=$(cd "arm9lib" && make clean && make 2>&1)
test_checksums "arm9lib/win_build/libarm9lib.a" "arm9lib/lib/libarm9lib.a"
comp_msg=$(cd "dldi" && make clean && make 2>&1)
test_checksums "dldi/win_build/dldi.dldi" "dldi/dldi.dldi"

if [ "${TOTAL_TESTS}" == "${TESTS_PASSED}" ]; then
  echo "All tests passed."
else
  echo -e "Make output for failed tests: ${OUTPUT_MSG}"
  echo -e "${SUMMARY}"
  echo "${TESTS_PASSED} out of ${TOTAL_TESTS} tests passed."
fi





