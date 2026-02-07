#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  AI Agent Dotfiles Installer${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if stow is installed
if ! command -v stow &> /dev/null; then
    echo -e "${RED}Error: GNU Stow is not installed${NC}"
    echo ""
    echo "Install it first:"
    echo "  macOS:  brew install stow"
    echo "  Linux:  sudo apt install stow  (or pacman -S stow)"
    exit 1
fi

# Get the directory where this script is located
DOTFILES_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${GREEN}Installing from:${NC} $DOTFILES_DIR"
echo ""

# Function to stow a package
stow_package() {
    local package=$1
    local description=$2

    echo -e "${YELLOW}Installing ${package}...${NC} ${description}"

    if stow -v -d "$DOTFILES_DIR" -t "$HOME" "$package" 2>&1 | grep -q "CONFLICT"; then
        echo -e "${RED}  ✗ Conflict detected${NC}"
        echo ""
        echo "  Existing files/directories conflict with $package"
        echo "  Options:"
        echo "    1. Backup existing files: mv ~/.$package ~/.$package.backup"
        echo "    2. Force overwrite: stow -D $package && stow $package"
        echo "    3. Skip this package"
        echo ""
        read -p "  Backup and continue? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ "$package" = "claude" ]; then
                mv ~/.claude ~/.claude.backup."$(date +%s)" 2>/dev/null || true
            elif [ "$package" = "opencode" ]; then
                mv ~/.config/opencode ~/.config/opencode.backup."$(date +%s)" 2>/dev/null || true
            fi
            stow -v -d "$DOTFILES_DIR" -t "$HOME" "$package"
            echo -e "${GREEN}  ✓ Installed (after backup)${NC}"
        else
            echo -e "${YELLOW}  ⊘ Skipped${NC}"
            return 1
        fi
    else
        stow -d "$DOTFILES_DIR" -t "$HOME" "$package"
        echo -e "${GREEN}  ✓ Installed${NC}"
    fi
    echo ""
}

# Install packages
stow_package "claude" "Claude Code configs → ~/.claude/"
stow_package "opencode" "OpenCode configs → ~/.config/opencode/"

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. ${YELLOW}Set up ~/.claude.json${NC} (if needed)"
echo "   This file may contain MCP servers, OAuth tokens, etc."
echo "   Use environment variables for API keys!"
echo ""
echo "2. ${YELLOW}Verify configs:${NC}"
echo "   ls -la ~/.claude/"
echo "   ls -la ~/.config/opencode/"
echo ""
echo "3. ${YELLOW}Start using:${NC}"
echo "   claude      # Launch Claude Code"
echo "   opencode    # Launch OpenCode"
echo ""
echo -e "${GREEN}Enjoy your AI coding agents!${NC}"
