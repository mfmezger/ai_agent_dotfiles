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
    echo "  Linux:  sudo apt install stow  (or paru -S stow)"
    exit 1
fi

# Get the directory where this script is located
DOTFILES_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${GREEN}Installing from:${NC} $DOTFILES_DIR"
echo ""

install_rtk() {
    echo -e "${YELLOW}Checking RTK...${NC} CLI proxy for token-optimized shell commands"

    if command -v rtk &> /dev/null; then
        echo -e "${GREEN}  ✓ Already installed${NC}"
        echo ""
        return 0
    fi

    if [[ "$OSTYPE" == darwin* ]] && command -v brew &> /dev/null; then
        echo "  Installing with Homebrew: brew install rtk"
        brew install rtk
    else
        echo "  Installing with the official RTK install script"
        curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
    fi

    if command -v rtk &> /dev/null; then
        echo -e "${GREEN}  ✓ Installed${NC}"
    else
        echo -e "${YELLOW}  ! Installed, but \`rtk\` is not on PATH in this shell${NC}"
        echo '  Add `export PATH="$HOME/.local/bin:$PATH"` to your shell config if needed'
    fi
    echo ""
}

# Function to stow a package
stow_package() {
    local package=$1
    local description=$2
    local dry_run_output
    local backup_target
    local timestamp

    echo -e "${YELLOW}Installing ${package}...${NC} ${description}"

    if dry_run_output="$(stow -n -v -d "$DOTFILES_DIR" -t "$HOME" "$package" 2>&1)"; then
        stow -d "$DOTFILES_DIR" -t "$HOME" "$package"
        echo -e "${GREEN}  ✓ Installed${NC}"
    else
        echo -e "${RED}  ✗ Stow detected a conflict or other install problem${NC}"
        echo ""
        echo "$dry_run_output"
        echo ""
        echo "  Existing files/directories conflict with $package"
        echo "  Options:"
        echo "    1. Backup existing files and continue"
        echo "    2. Skip this package"
        echo ""
        read -p "  Backup and continue? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            timestamp="$(date +%s)"
            if [[ "$package" = "claude" ]]; then
                backup_target="$HOME/.claude"
            elif [[ "$package" = "opencode" ]]; then
                backup_target="$HOME/.config/opencode"
            elif [[ "$package" = "codex" ]]; then
                backup_target="$HOME/.codex"
            elif [[ "$package" = "gemini" ]]; then
                backup_target="$HOME/.gemini"
            elif [[ "$package" = "pi" ]]; then
                backup_target="$HOME/.pi"
            fi

            if [[ -n "$backup_target" && -e "$backup_target" ]]; then
                mv "$backup_target" "$backup_target.backup.$timestamp"
                echo "  Backed up $backup_target to $backup_target.backup.$timestamp"
            fi

            stow -v -d "$DOTFILES_DIR" -t "$HOME" "$package"
            echo -e "${GREEN}  ✓ Installed (after backup)${NC}"
        else
            echo -e "${YELLOW}  ⊘ Skipped${NC}"
            return 1
        fi
    fi
    echo ""
}

# Install packages
install_rtk
stow_package "claude" "Claude Code configs → ~/.claude/"
stow_package "opencode" "OpenCode configs → ~/.config/opencode/"
stow_package "codex" "Codex CLI configs → ~/.codex/"
stow_package "gemini" "Gemini CLI configs → ~/.gemini/"
stow_package "pi" "pi coding agent configs → ~/.pi/"

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
echo "   ls -la ~/.codex/"
echo "   ls -la ~/.gemini/"
echo "   ls -la ~/.pi/agent/"
echo ""
echo "3. ${YELLOW}Start using:${NC}"
echo "   claude      # Launch Claude Code"
echo "   opencode    # Launch OpenCode"
echo "   codex       # Launch Codex CLI"
echo "   gemini      # Launch Gemini CLI"
echo "   pi          # Launch pi coding agent"
echo ""
echo -e "${GREEN}Enjoy your AI coding agents!${NC}"
