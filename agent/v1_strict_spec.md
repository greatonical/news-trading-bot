## MULTI-ASSET TRADING (VERSION 1.0)

STATUS:

- INCLUDED in V1.0
- DISABLED by default

RULES:

- Assets must come exclusively from pre-mapped news asset sets
- Max assets per event: 3 (hard limit)
- Aggregate risk per event MUST NOT exceed:
  - 1.0% in LOW_RISK mode
  - 0.5% in HIGH_RISK mode
- Aggregate risk is split evenly across all selected assets
- Global risk rules (daily loss, consecutive losses, spread guards) ALWAYS apply
- Correlation risk is explicitly acknowledged and documented

FORBIDDEN:

- Dynamic asset discovery or runtime symbol selection
- Unlimited or unbounded positions per event
- Aggregate risk exceeding defined per-event limits
- Bypassing or weakening the global risk engine
