# AI_trading_ADA

Hermes Agent specialized for trading **only Cardano (ADA)**.

Based on [Nous Research Hermes Agent](https://github.com/NousResearch/hermes-agent) — a self-improving AI agent runtime with persistent memory, skill learning, and multi-platform support.

## Goal

Build a dedicated AI trading agent that:
- Analyzes only ADA (price, volume, technicals, news, on-chain)
- Generates buy/sell/hold signals with risk management
- Defaults to paper/dry-run trading
- Learns and improves its own skills over time
- Supports HITL (human-in-the-loop) for any live execution

## Quick Start

1. Install Hermes Agent:
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

2. Clone this repo and place custom skills into your Hermes skills directory.

3. Configure API keys for data sources (e.g. Binance, CoinGecko, or Cardano-specific APIs) in `.env`.

4. Run the agent and invoke the ADA skill:
   ```bash
   hermes
   /ada-trader analyze
   ```

## Project Structure

- `skills/ada-trader/` — Custom skill for ADA-only trading logic
- `config/` — Example configuration
- `docs/` — Development notes and strategy ideas

## Safety

- Never auto-execute live trades without explicit user confirmation.
- Start with paper trading only.
- Risk limits: max position size, stop-loss, drawdown halt.

## Status

Early development. Custom skills and data integrations to be expanded.

---

Created for developing an ADA-focused Hermes Agent.
