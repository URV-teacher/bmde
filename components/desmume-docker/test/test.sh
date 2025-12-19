set -e

export ROOT="$(cd "$(dirname "$(realpath "$0")")/.." &>/dev/null && pwd)"
echo "Root folder is ${ROOT}"

if [ "$EUID" -ne 0 ]; then
  echo "❌ This script must be run as root. Exiting."
  exit 1
fi

mount "${ROOT}/fs/fat.img" "${ROOT}/fs/mountpoint"

if [ -f "${ROOT}/fs/mountpoint/output.txt" ]; then
  echo "output.txt detected, removing"
  rm "${ROOT}/fs/mountpoint/output.txt"
  umount "${ROOT}/fs/mountpoint"
  mount "${ROOT}/fs/fat.img" "${ROOT}/fs/mountpoint"
  [ -f "${ROOT}/fs/mountpoint/output.txt" ] && echo "The file is present after deleting, something is wrong" && exit 1
fi

umount "${ROOT}/fs/mountpoint"
{
  cd "${ROOT}"
  echo "root: ${ROOT}"
  BUILDKIT_PROGRESS=plain docker compose up --build -d
}

mount "${ROOT}/fs/fat.img" "${ROOT}/fs/mountpoint"
while [ ! -f "${ROOT}/fs/mountpoint/output.txt" ]; do
  umount "${ROOT}/fs/mountpoint"
  echo "output.txt still not detected"
  sleep 1
  mount "${ROOT}/fs/fat.img" "${ROOT}/fs/mountpoint"
done

echo "output.txt detected, test passed"
rm "${ROOT}/fs/mountpoint/output.txt"
umount "${ROOT}/fs/mountpoint"
exit 0





