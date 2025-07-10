#!/bin/bash
set -e

# ── Core metadata ─────────────────────────────────────────────────────────────
APP_NAME="mongodbexporter"
EXECUTABLE="MongoDBExporter"  # ✅ Make sure this matches your PyInstaller output exactly
VERSION="2.3.0"
ARCH="$(dpkg --print-architecture)"
MAINTAINER="Sarwar Hossain <sarwarhridoy4@gmail.com>"
HOMEPAGE="https://github.com/Sarwarhridoy4/MongoDB-Exporter"
DESCRIPTION="MongoDB Exporter GUI is a Python-based application with a simple graphical user interface (GUI) for exporting collections from a MongoDB database to JSON files. This tool allows users to connect to their MongoDB database, select the database they want to export, and specify the output directory where the JSON files will be saved. The application also provides real-time progress updates, including the name of the current collection being exported and the percentage of the export process completed."

DIST_DIR="dist"
BUILD_DIR="${APP_NAME}-deb"
ICON_SRC="asset/favicon.png"  # ✅ Ensure this file exists
ICON_NAME="appicon.png"        # ✅ Final icon name to be used in desktop entry

# ── Clean old build ───────────────────────────────────────────────────────────
echo "🧹 Cleaning previous build ..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"/usr/bin
mkdir -p "${BUILD_DIR}"/usr/share/applications
mkdir -p "${BUILD_DIR}"/usr/share/icons/hicolor/256x256/apps
mkdir -p "${BUILD_DIR}"/usr/share/doc/${APP_NAME}
mkdir -p "${BUILD_DIR}"/DEBIAN

# ── Copy PyInstaller binary ───────────────────────────────────────────────────
echo "📁 Copying PyInstaller onefile binary ..."
cp "${DIST_DIR}/${EXECUTABLE}" "${BUILD_DIR}/usr/bin/"
chmod +x "${BUILD_DIR}/usr/bin/${EXECUTABLE}"

# ── Install icon ──────────────────────────────────────────────────────────────
echo "🖼 Installing icon ..."
cp "${ICON_SRC}" "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/${ICON_NAME}"
chmod 644 "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/${ICON_NAME}"

# ── Create .desktop file ──────────────────────────────────────────────────────
echo "📄 Creating .desktop file ..."
cat > "${BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=MongoDB Exporter
Exec=/usr/bin/${EXECUTABLE}
Icon=${ICON_NAME}
Terminal=false
Categories=Database;Utility;
StartupNotify=true
EOF
chmod 644 "${BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop"

# ── Create DEBIAN control file ────────────────────────────────────────────────
echo "📜 Creating control file ..."
cat > "${BUILD_DIR}/DEBIAN/control" <<EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: libc6 (>= 2.31)
Maintainer: ${MAINTAINER}
Homepage: ${HOMEPAGE}
Description: ${DESCRIPTION}
 MongoDB Exporter is a graphical tool for exporting non-empty collections
 from MongoDB databases to JSON format with real-time progress indication.
EOF

# ── Optional: copy docs ───────────────────────────────────────────────────────
if [[ -f README.md ]]; then
  cp README.md "${BUILD_DIR}/usr/share/doc/${APP_NAME}/README"
  gzip -9 "${BUILD_DIR}/usr/share/doc/${APP_NAME}/README"
fi

if [[ -f LICENSE ]]; then
  cp LICENSE "${BUILD_DIR}/usr/share/doc/${APP_NAME}/copyright"
  gzip -9 "${BUILD_DIR}/usr/share/doc/${APP_NAME}/copyright"
fi

# ── Permissions ───────────────────────────────────────────────────────────────
chmod -R 755 "${BUILD_DIR}/usr"
chmod 755 "${BUILD_DIR}/DEBIAN"

# ── Build .deb ────────────────────────────────────────────────────────────────
echo "📦 Building Debian package ..."
dpkg-deb --build "${BUILD_DIR}"
DEB_FILE="${APP_NAME}_${VERSION}_${ARCH}.deb"
mv "${BUILD_DIR}.deb" "${DEB_FILE}"

# ── Install & update icon cache ───────────────────────────────────────────────
echo "📥 Installing ${DEB_FILE} ..."
sudo dpkg -i "${DEB_FILE}" || true  # Allow dependency warnings (not needed for PyInstaller builds)

echo "🔄 Updating icon cache ..."
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor || true

echo "✅ Done! MongoDB Exporter should now appear in your system menu."
echo "🚀 Launch it from menu or run: ${EXECUTABLE}"
