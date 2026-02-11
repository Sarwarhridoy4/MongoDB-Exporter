#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper. Use unified Linux builder.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/build_linux.sh" --appimage "$@"
