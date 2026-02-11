#!/usr/bin/env bash
set -Eeuo pipefail

# Unified Linux build script for MongoDB Exporter
# Builds:
#   1) Debian package (.deb)
#   2) AppImage
#
# Usage:
#   ./build_linux.sh                 # build both targets
#   ./build_linux.sh --all           # same as default
#   ./build_linux.sh --deb           # build only .deb
#   ./build_linux.sh --appimage      # build only AppImage
#   ./build_linux.sh --clean         # remove build artifacts and exit
#
# Optional environment overrides:
#   VERSION=2.4.0 APP_NAME=mongodbexporter EXECUTABLE=MongoDBExporter ./build_linux.sh --all

APP_NAME="${APP_NAME:-mongodbexporter}"
EXECUTABLE="${EXECUTABLE:-MongoDBExporter}"
VERSION="${VERSION:-2.4.0}"
MAINTAINER="${MAINTAINER:-Sarwar Hossain <sarwarhridoy4@gmail.com>}"
HOMEPAGE="${HOMEPAGE:-https://github.com/Sarwarhridoy4/MongoDB-Exporter}"
SECTION="${SECTION:-utils}"
PRIORITY="${PRIORITY:-optional}"
DESCRIPTION_SHORT="${DESCRIPTION_SHORT:-MongoDB Exporter GUI for MongoDB backup export, compression, and encryption}"
DESCRIPTION_LONG="${DESCRIPTION_LONG:-MongoDB Exporter is a PySide6 desktop tool to export MongoDB collections to JSON with progress tracking, optional ZIP compression, and optional AES-GCM encryption/decryption workflows.}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_FILE="${ROOT_DIR}/main.spec"
DIST_DIR="${ROOT_DIR}/dist"
BUILD_DIR="${ROOT_DIR}/build"
RELEASE_DIR="${ROOT_DIR}/release"
TOOLS_DIR="${ROOT_DIR}/.tools"
ASSET_ICON="${ROOT_DIR}/asset/favicon.png"

TARGET="all"

log() {
  printf '[build] %s\n' "$*"
}

fail() {
  printf '[build][error] %s\n' "$*" >&2
  exit 1
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

usage() {
  cat <<USAGE
Usage: ./build_linux.sh [--all|--deb|--appimage|--clean]

Options:
  --all        Build both Debian and AppImage (default)
  --deb        Build only Debian package
  --appimage   Build only AppImage
  --clean      Remove build artifacts and exit
  -h, --help   Show this help
USAGE
}

parse_args() {
  if [[ $# -eq 0 ]]; then
    TARGET="all"
    return
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --all) TARGET="all" ;;
      --deb) TARGET="deb" ;;
      --appimage) TARGET="appimage" ;;
      --clean) TARGET="clean" ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        fail "Unknown argument: $1"
        ;;
    esac
    shift
  done
}

clean_artifacts() {
  log "Cleaning build artifacts"
  rm -rf "${BUILD_DIR}" "${RELEASE_DIR}" "${ROOT_DIR}/AppDir" "${DIST_DIR}" "${ROOT_DIR}/${APP_NAME}.AppImage"
}

require_core_tools() {
  has_cmd python3 || fail "python3 is required"
  has_cmd pyinstaller || fail "pyinstaller is required (install via: pip install pyinstaller)"
}

build_binary() {
  [[ -f "${SPEC_FILE}" ]] || fail "Spec file not found: ${SPEC_FILE}"
  [[ -f "${ASSET_ICON}" ]] || fail "Icon not found: ${ASSET_ICON}"

  log "Building PyInstaller executable from ${SPEC_FILE}"
  pyinstaller --noconfirm --clean "${SPEC_FILE}"

  [[ -f "${DIST_DIR}/${EXECUTABLE}" ]] || fail "Expected binary missing: ${DIST_DIR}/${EXECUTABLE}"
}

write_desktop_entry() {
  local desktop_file="$1"
  cat > "${desktop_file}" <<DESKTOP
[Desktop Entry]
Type=Application
Name=MongoDB Exporter
Comment=${DESCRIPTION_SHORT}
Exec=${EXECUTABLE}
Icon=${APP_NAME}
Terminal=false
Categories=Database;Utility;
StartupNotify=true
DESKTOP
}

build_deb() {
  has_cmd dpkg-deb || fail "dpkg-deb is required for Debian package build"

  local arch
  arch="$(dpkg --print-architecture)"

  local pkgroot
  pkgroot="${BUILD_DIR}/deb/${APP_NAME}_${VERSION}_${arch}"

  log "Preparing Debian package structure"
  rm -rf "${pkgroot}"
  mkdir -p \
    "${pkgroot}/DEBIAN" \
    "${pkgroot}/usr/bin" \
    "${pkgroot}/usr/share/applications" \
    "${pkgroot}/usr/share/icons/hicolor/256x256/apps" \
    "${pkgroot}/usr/share/doc/${APP_NAME}"

  install -m 0755 "${DIST_DIR}/${EXECUTABLE}" "${pkgroot}/usr/bin/${EXECUTABLE}"
  install -m 0644 "${ASSET_ICON}" "${pkgroot}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"

  write_desktop_entry "${pkgroot}/usr/share/applications/${APP_NAME}.desktop"

  cat > "${pkgroot}/DEBIAN/control" <<CONTROL
Package: ${APP_NAME}
Version: ${VERSION}
Section: ${SECTION}
Priority: ${PRIORITY}
Architecture: ${arch}
Maintainer: ${MAINTAINER}
Homepage: ${HOMEPAGE}
Depends: libc6 (>= 2.31), libglib2.0-0, libx11-6, libstdc++6
Description: ${DESCRIPTION_SHORT}
 ${DESCRIPTION_LONG}
CONTROL

  if [[ -f "${ROOT_DIR}/README.md" ]]; then
    install -m 0644 "${ROOT_DIR}/README.md" "${pkgroot}/usr/share/doc/${APP_NAME}/README.md"
    gzip -n -f "${pkgroot}/usr/share/doc/${APP_NAME}/README.md"
  fi

  if [[ -f "${ROOT_DIR}/License.lic" ]]; then
    install -m 0644 "${ROOT_DIR}/License.lic" "${pkgroot}/usr/share/doc/${APP_NAME}/copyright"
    gzip -n -f "${pkgroot}/usr/share/doc/${APP_NAME}/copyright"
  fi

  mkdir -p "${RELEASE_DIR}"
  local output_deb="${RELEASE_DIR}/${APP_NAME}_${VERSION}_${arch}.deb"

  log "Building Debian package: ${output_deb}"
  dpkg-deb --build --root-owner-group "${pkgroot}" "${output_deb}"
}

resolve_appimagetool() {
  local arch
  arch="$(uname -m)"

  if has_cmd appimagetool; then
    command -v appimagetool
    return
  fi

  mkdir -p "${TOOLS_DIR}"
  local tool="${TOOLS_DIR}/appimagetool-${arch}.AppImage"

  if [[ ! -x "${tool}" ]]; then
    has_cmd curl || fail "curl is required to download appimagetool"
    local url="https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-${arch}.AppImage"
    log "Downloading appimagetool: ${url}"
    curl -fL "${url}" -o "${tool}"
    chmod +x "${tool}"
  fi

  printf '%s\n' "${tool}"
}

build_appimage() {
  local arch
  arch="$(uname -m)"

  local appdir
  appdir="${BUILD_DIR}/appimage/AppDir"

  log "Preparing AppDir"
  rm -rf "${appdir}" "${ROOT_DIR}/${APP_NAME}.AppImage"
  rm -f "${ROOT_DIR}"/*.AppImage
  mkdir -p \
    "${appdir}/usr/bin" \
    "${appdir}/usr/share/applications" \
    "${appdir}/usr/share/icons/hicolor/256x256/apps"

  install -m 0755 "${DIST_DIR}/${EXECUTABLE}" "${appdir}/usr/bin/${EXECUTABLE}"
  install -m 0644 "${ASSET_ICON}" "${appdir}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
  install -m 0644 "${ASSET_ICON}" "${appdir}/${APP_NAME}.png"

  write_desktop_entry "${appdir}/${APP_NAME}.desktop"
  install -m 0644 "${appdir}/${APP_NAME}.desktop" "${appdir}/usr/share/applications/${APP_NAME}.desktop"

  cat > "${appdir}/AppRun" <<'APPRUN'
#!/usr/bin/env bash
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${HERE}/usr/bin/MongoDBExporter" "$@"
APPRUN
  chmod +x "${appdir}/AppRun"

  local appimagetool
  appimagetool="$(resolve_appimagetool)"

  mkdir -p "${RELEASE_DIR}"
  local output_img="${RELEASE_DIR}/${APP_NAME}-${VERSION}-${arch}.AppImage"

  log "Building AppImage: ${output_img}"
  ARCH="${arch}" "${appimagetool}" "${appdir}"

  local produced_img=""
  if [[ -f "${ROOT_DIR}/${APP_NAME}.AppImage" ]]; then
    produced_img="${ROOT_DIR}/${APP_NAME}.AppImage"
  else
    local candidates=("${ROOT_DIR}"/*.AppImage)
    if [[ ${#candidates[@]} -gt 0 && -f "${candidates[0]}" ]]; then
      produced_img="$(ls -t "${ROOT_DIR}"/*.AppImage | head -n 1)"
    fi
  fi

  [[ -n "${produced_img}" ]] || fail "AppImage produced, but output file was not found in ${ROOT_DIR}"
  mv "${produced_img}" "${output_img}"
  chmod +x "${output_img}"
}

main() {
  parse_args "$@"

  if [[ "${TARGET}" == "clean" ]]; then
    clean_artifacts
    log "Clean completed"
    exit 0
  fi

  require_core_tools
  build_binary

  case "${TARGET}" in
    all)
      build_deb
      build_appimage
      ;;
    deb)
      build_deb
      ;;
    appimage)
      build_appimage
      ;;
    *)
      fail "Unsupported target: ${TARGET}"
      ;;
  esac

  log "Build completed. Artifacts are in: ${RELEASE_DIR}"
}

main "$@"
