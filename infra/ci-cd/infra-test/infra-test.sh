#!/bin/bash

REQUIRED_NODE_VERSION="18"
CURRENT_NODE_VERSION=$(node -v | cut -d'v' -f2)

if [[ "$CURRENT_NODE_VERSION" != "$REQUIRED_NODE_VERSION"* ]]; then
  echo " Node.js version mismatch! Required: $REQUIRED_NODE_VERSION"
  exit 1
fi

echo " All infrastructure requirements met"
