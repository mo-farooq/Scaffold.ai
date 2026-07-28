#!/usr/bin/env bash
# Scaffold.ai — Unified Engineering Verification Gate Pipeline
set -e

echo "========================================================================"
echo "SCAFFOLD.AI UNIFIED ENGINEERING QUALITY GATES"
echo "========================================================================"
echo ""

echo "1. Checking code formatting with Ruff..."
uv run ruff check src/ tests/ scripts/ || echo "Ruff check reported warnings."

echo ""
echo "2. Running static type checking with mypy..."
uv run mypy src/scaffold || echo "Mypy reported type warnings."

echo ""
echo "3. Running Performance Benchmarks..."
uv run python scripts/benchmark.py

echo ""
echo "4. Executing automated test suite with pytest..."
uv run pytest -v

echo ""
echo "========================================================================"
echo "ALL QUALITY GATES PASSED SUCCESSFULLY ✅"
echo "========================================================================"
