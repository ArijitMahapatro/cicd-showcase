#!/bin/bash
# .git/hooks/pre-commit
# Install: cp scripts/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#
# Demonstrates: Git hooks, programmatic commit management (JD requirement)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Running pre-commit checks...${NC}"

ERRORS=0

# ── 1. Check for secrets / API keys ───────────────────────────────────────
echo -n "  Checking for secrets... "
PATTERNS=(
    "AKIA[0-9A-Z]{16}"
    "sk-[a-zA-Z0-9]{32,}"
    "ghp_[a-zA-Z0-9]{36}"
    "password\s*=\s*['\"][^'\"]{8,}"
    "api_key\s*=\s*['\"][^'\"]{8,}"
)

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
SECRET_FOUND=0

for file in $STAGED_FILES; do
    for pattern in "${PATTERNS[@]}"; do
        if git show ":$file" 2>/dev/null | grep -qE "$pattern"; then
            echo -e "${RED}FAIL${NC}"
            echo -e "  ${RED}Potential secret found in: $file${NC}"
            SECRET_FOUND=1
            ERRORS=$((ERRORS + 1))
            break
        fi
    done
done

[ $SECRET_FOUND -eq 0 ] && echo -e "${GREEN}OK${NC}"

# ── 2. Lint frontend JS/JSX files if changed ─────────────────────────────
FRONTEND_FILES=$(echo "$STAGED_FILES" | grep -E "^frontend/src/.*\.(js|jsx|ts|tsx)$" || true)

if [ -n "$FRONTEND_FILES" ]; then
    echo -n "  ESLint check... "
    if command -v npx &>/dev/null; then
        cd frontend
        if npx eslint $FRONTEND_FILES --quiet 2>/dev/null; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${YELLOW}WARNINGS (non-blocking)${NC}"
        fi
        cd ..
    else
        echo -e "${YELLOW}SKIP (npx not found)${NC}"
    fi
fi

# ── 3. Validate Terraform if .tf files changed ────────────────────────────
TF_FILES=$(echo "$STAGED_FILES" | grep -E "\.tf$" || true)

if [ -n "$TF_FILES" ]; then
    echo -n "  Terraform fmt check... "
    if command -v terraform &>/dev/null; then
        if terraform fmt -check -recursive infra/terraform/ 2>/dev/null; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${RED}FAIL — run: terraform fmt -recursive infra/terraform/${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${YELLOW}SKIP (terraform not installed)${NC}"
    fi
fi

# ── 4. Check for debug statements ────────────────────────────────────────
echo -n "  Checking for debug statements... "
DEBUG_FOUND=0
for file in $STAGED_FILES; do
    if echo "$file" | grep -qE "\.(js|jsx|ts|tsx)$"; then
        if git show ":$file" 2>/dev/null | grep -qE "console\.(log|debug|warn)\(|debugger"; then
            if [ $DEBUG_FOUND -eq 0 ]; then
                echo -e "${YELLOW}WARN${NC}"
            fi
            echo -e "  ${YELLOW}Debug statement found in: $file${NC}"
            DEBUG_FOUND=1
        fi
    fi
done
[ $DEBUG_FOUND -eq 0 ] && echo -e "${GREEN}OK${NC}"

# ── Result ────────────────────────────────────────────────────────────────
echo ""
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Pre-commit failed with $ERRORS error(s). Commit blocked.${NC}"
    echo -e "To bypass (not recommended): git commit --no-verify"
    exit 1
else
    echo -e "${GREEN}All pre-commit checks passed. Proceeding with commit.${NC}"
    exit 0
fi
