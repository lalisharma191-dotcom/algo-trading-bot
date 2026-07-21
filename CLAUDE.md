# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and other AI assistants when working with code in this repository.

## Repository Overview

**algo-trading-bot** is a Python-based Binance trading bot using an RSI, EMA, and MACD strategy with risk management.

> **Current state:** This repository is at its initial stage. It contains only `README.md` — no source code, dependencies, configuration, or tests exist yet. The sections below describe the project's stated intent and the conventions to follow as the codebase is built out. Update this file as real structure lands.

## Current Structure

```
algo-trading-bot/
├── README.md    # One-line project description
└── CLAUDE.md    # This file
```

There is no build system, package manifest (`requirements.txt` / `pyproject.toml`), test suite, linter configuration, or CI workflow yet.

## Intended Domain

Per the README, the project will be:

- **Language:** Python
- **Exchange:** Binance (typically via a client library such as `python-binance` or `ccxt`)
- **Strategy:** Technical-indicator based — RSI (Relative Strength Index), EMA (Exponential Moving Average), and MACD (Moving Average Convergence Divergence)
- **Risk management:** Position sizing, stop-loss / take-profit logic

## Conventions for AI Assistants

Since the codebase does not exist yet, follow these principles when adding code:

### Project setup
- Use a standard Python layout: a package directory (e.g. `bot/` or `src/`), `tests/`, and a `requirements.txt` or `pyproject.toml` at the root.
- Pin dependencies when adding a manifest.
- Add a `.gitignore` for Python (`__pycache__/`, `.env`, virtual envs) before committing any code.

### Security — critical for a trading bot
- **Never commit API keys or secrets.** Binance API credentials must come from environment variables or a git-ignored `.env` file. Provide a `.env.example` with placeholder values instead.
- Default to **Binance testnet** or paper-trading mode in examples and default configuration; live trading should require explicit opt-in.
- Keep withdrawal permissions off API keys; document this in setup instructions.

### Trading-logic guidelines
- Keep strategy logic (indicator calculation, signal generation) separate from execution logic (order placement) and from risk management (position sizing, stop-loss), so each can be unit-tested without hitting the exchange.
- Indicator math (RSI, EMA, MACD) should be deterministic and covered by unit tests with known input/output fixtures — no network calls in tests.
- Handle exchange errors defensively: rate limits, partial fills, network timeouts, and clock drift are normal operating conditions, not edge cases.
- Use `Decimal` or exchange-provided precision rules for quantities and prices; never send raw floats that violate Binance lot-size/tick-size filters.

### Git workflow
- The default branch is `main`.
- Develop on feature branches; keep commits small with clear, descriptive messages.
- Do not commit generated data, logs, or backtest output artifacts.

## Verification

There are no tests or linters configured yet. When they are added, document the exact commands here (e.g. `pytest`, `ruff check .`) so assistants can verify changes before committing.
