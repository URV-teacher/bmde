#!/usr/bin/env bash
# Runs the tests of every component inside the full development environment image, with the components mounted in
# /components. These are the same tests that the CI of each component runs in its own image and in a host.
#   shell/test.sh [IMAGE]    (aleixmt/bmde-full:latest by default)
set -Eeuo pipefail

IMAGE="${1:-aleixmt/bmde-full:latest}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Tests that need the credentials of a user of the course
MANUAL_TESTS=" git-urv-vpn-docker/scripts/test_operation.sh "

failed=()
for test in "${ROOT}"/components/*/scripts/test_*.sh; do
  test="${test#"${ROOT}/components/"}"
  if [[ "${MANUAL_TESTS}" == *" ${test} "* ]]; then
    continue
  fi
  echo "::group::${test}"
  if ! docker run --rm -v "${ROOT}/components:/components:ro" --entrypoint bash "${IMAGE}" "/components/${test}"; then
    failed+=("${test}")
  fi
  echo "::endgroup::"
done

if (( ${#failed[@]} > 0 )); then
  echo "Failed tests: ${failed[*]}"
  exit 1
fi
echo "All tests passed"
