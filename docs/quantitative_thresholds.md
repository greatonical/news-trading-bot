# QUANTITATIVE THRESHOLDS - VERSION 1.0

**Last Updated:** 2025-12-30  
**Status:** Implementation-Ready  
**Purpose:** All numeric constants and decision thresholds for the V1 trading system

---

## 1. VOLATILITY DETECTION (LOW_RISK MODE)

**Purpose:** Detect abnormal market reaction to news events

**Metric:** 1-minute candle range expansion

**Formula:**

```
current_1min_range = high - low of current candle
avg_1min_range = average(last 60 candles' ranges)

volatility_detected = current_1min_range >= (2.0 × avg_1min_range)
```

**Parameters:**

- **Lookback period:** 60 minutes (60 candles on 1-min chart)
- **Threshold multiplier:** 2.0×
- **Timeframe:** 1-minute candles exclusively

**Application:**

- Must be TRUE for LOW_RISK trade to proceed
- Checked continuously during news window
- First candle meeting threshold = "reaction candle"

---

## 2. DIRECTION CONFIRMATION (LOW_RISK MODE)

**Purpose:** Avoid first-candle fakeouts

**Rule:** Price must "accept" the initial move before entry

**Precise Definition:**

```
reaction_candle_open = open price of reaction candle
reaction_candle_range = high - low of reaction candle
next_candle_close = close of candle immediately after reaction candle

For LONG bias:
  direction_confirmed = next_candle_close > (reaction_candle_open + 0.5 × reaction_candle_range)

For SHORT bias:
  direction_confirmed = next_candle_close < (reaction_candle_open - 0.5 × reaction_candle_range)
```

**What This Means:**

- If reaction candle moves up, next candle must close in upper 50% of that range
- If reaction candle moves down, next candle must close in lower 50% of that range
- Prevents entry if price immediately retraces more than halfway

**Example (LONG):**

- Reaction candle: Open 1.0800, High 1.0850, Low 1.0795
- Range = 55 pips
- Midpoint = 1.0800 + (55/2) = 1.0827.5
- Next candle must close above 1.0827.5 to confirm LONG

---

## 3. SPREAD GUARDS (ALL MODES)

**Purpose:** Avoid execution during abnormal liquidity conditions

**Rule:** Current spread must not exceed 3× average spread

**Formula:**

```
avg_spread = average(bid-ask spread over last 60 minutes)
current_spread = current_ask - current_bid

spread_acceptable = current_spread <= (3.0 × avg_spread)
```

**Parameters:**

- **Averaging period:** 60 minutes
- **Threshold multiplier:** 3.0×
- **Measurement frequency:** Every tick during news window

**Per-Asset Absolute Limits (Emergency Override):**

| Asset  | Max Spread (pips) | Notes                   |
| ------ | ----------------- | ----------------------- |
| EURUSD | 5.0               | Typical: 0.5-1.5 pips   |
| GBPUSD | 6.0               | Typical: 1.0-2.0 pips   |
| USDJPY | 5.0               | Typical: 0.5-1.5 pips   |
| XAUUSD | 100               | Typical: 20-40 cents    |
| NAS100 | 5.0               | Typical: 1.0-2.0 points |
| US30   | 8.0               | Typical: 2.0-4.0 points |

**If spread exceeds either the 3× average OR the absolute limit → NO TRADE**

---

## 4. RISK LIMITS (GLOBAL)

**Purpose:** Protect capital through hard constraints

### Per-Trade Risk

| Mode      | Risk per Trade | Notes                         |
| --------- | -------------- | ----------------------------- |
| LOW_RISK  | 1.0%           | Default and primary mode      |
| HIGH_RISK | 0.5%           | Reduced due to execution risk |

### Daily Risk

- **Daily loss limit:** 3.0% of account balance
- **Calculation:** Cumulative realized P&L for the current trading day
- **Action when hit:** System stops trading until next day (manual override required)

### Consecutive Loss Protection

- **Max consecutive losses:** 3
- **Definition:** 3 trades in a row hitting stop loss
- **Action:** System pauses, requires manual review before resuming
- **Purpose:** Detect broken logic or adverse market regime

### Position Limits

- **Max open positions (total):** 3
- **Max positions per base currency:** 2
  - Example: Can't have EURUSD + EURGBP + EURJPY simultaneously
- **Max positions per news event:** 3 (only if multi-asset enabled)

---

## 5. MULTI-ASSET RISK ALLOCATION (IF ENABLED)

**Purpose:** Split risk safely across correlated assets

### Aggregate Risk Cap

| Mode      | Total Risk per Event | Distribution Rule            |
| --------- | -------------------- | ---------------------------- |
| LOW_RISK  | 1.0%                 | Divided evenly across assets |
| HIGH_RISK | 0.5%                 | Divided evenly across assets |

### Formula

```
num_selected_assets = number of assets chosen for this event (1-3)
risk_per_asset = total_event_risk / num_selected_assets
```

### Examples

**Scenario 1: LOW_RISK, 2 assets**

- Total event risk: 1.0%
- EURUSD risk: 0.5%
- XAUUSD risk: 0.5%

**Scenario 2: HIGH_RISK, 3 assets**

- Total event risk: 0.5%
- EURUSD risk: 0.167%
- USDJPY risk: 0.167%
- XAUUSD risk: 0.166%

### Constraints

- **Max assets per event:** 3 (hard limit)
- **Correlation warning:** User must acknowledge USD-based pairs are highly correlated
- **Independent execution:** Each asset trades independently within its risk allocation

---

## 6. POSITION SIZE CALCULATION

**Purpose:** Convert risk percentage to actual lot size

### Formula

```
account_balance = current MT5 account balance
risk_amount = account_balance × risk_percentage
stop_loss_distance = entry_price - stop_loss_price (absolute value)
pip_value = standard pip value for asset and lot size
position_size = risk_amount / (stop_loss_distance × pip_value)
```

### Stop Loss Calculation

```
reaction_candle_range = reaction_candle_high - reaction_candle_low
stop_loss_distance = 1.5 × reaction_candle_range

For LONG:
  stop_loss_price = entry_price - stop_loss_distance

For SHORT:
  stop_loss_price = entry_price + stop_loss_distance
```

### Take Profit Calculation

```
take_profit_distance = 2.0 × stop_loss_distance

For LONG:
  take_profit_price = entry_price + take_profit_distance

For SHORT:
  take_profit_price = entry_price - take_profit_distance
```

**Risk:Reward Ratio:** Minimum 1:2 (enforced by 2× multiplier)

---

## 7. NORMALIZED MOVE (MULTI-ASSET SELECTION)

**Purpose:** Compare reaction magnitude across different assets fairly

### Formula

```
For each mapped asset during a news event:

  current_move_pips = abs(current_price - pre_news_price)
  avg_1min_range = average(last 60 × 1-min candle ranges for this asset)

  normalized_move = current_move_pips / avg_1min_range
```

### Auto-Selection Rule (if multi-asset enabled with auto mode)

```
1. Calculate normalized_move for all mapped assets
2. Rank by normalized_move (highest to lowest)
3. Select top N assets (where N = user-configured max, 1-3)
4. Apply risk allocation to selected assets
```

### Example

**USD CPI event, mapped assets: EURUSD, USDJPY, XAUUSD**

| Asset  | Current Move | Avg 1-min Range | Normalized Move | Rank |
| ------ | ------------ | --------------- | --------------- | ---- |
| XAUUSD | 8.50         | 2.10            | 4.05            | 1    |
| EURUSD | 12.00        | 3.50            | 3.43            | 2    |
| USDJPY | 18.00        | 5.80            | 3.10            | 3    |

**If user selected max 2 assets → Trade XAUUSD and EURUSD**

---

## 8. EVENT DEVIATION THRESHOLDS (HIGH_RISK MODE)

**Purpose:** Determine when news outcome is "significant enough" for immediate execution

### Deviation Table

| Event                      | Threshold              | Example                                       |
| -------------------------- | ---------------------- | --------------------------------------------- |
| **CPI (YoY)**              | ±0.3%                  | Forecast 3.2%, actual ≥3.5% or ≤2.9%          |
| **Core CPI (YoY)**         | ±0.3%                  | Forecast 3.0%, actual ≥3.3% or ≤2.7%          |
| **NFP**                    | ±50K jobs              | Forecast 200K, actual ≥250K or ≤150K          |
| **Unemployment Rate**      | ±0.2%                  | Forecast 4.1%, actual ≥4.3% or ≤3.9%          |
| **Fed Interest Rate**      | ±25 bps OR qualitative | Rate change or statement hawkish/dovish shift |
| **GDP (QoQ)**              | ±0.5%                  | Forecast 2.5%, actual ≥3.0% or ≤2.0%          |
| **Retail Sales**           | ±0.4%                  | Forecast 0.5%, actual ≥0.9% or ≤0.1%          |
| **PMI (Manufacturing)**    | ±2.0 points            | Forecast 51.0, actual ≥53.0 or ≤49.0          |
| **Trade Balance**          | ±$5B                   | Forecast -$60B, actual ≥-$55B or ≤-$65B       |
| **Initial Jobless Claims** | ±20K                   | Forecast 220K, actual ≥240K or ≤200K          |

### High-Risk Logic

```
deviation = abs(actual - forecast)

if deviation >= threshold:
    high_risk_qualified = True
else:
    high_risk_qualified = False
    revert_to_low_risk()
```

### Notes

- Thresholds are conservative (institutional-grade significance)
- Not every high-impact event qualifies for HIGH_RISK execution
- If threshold not met → system automatically aborts and reverts to LOW_RISK
- User cannot override deviation checks

---

## 9. TIME-BASED RULES

### News Window

- **Definition:** Period during which LOW_RISK mode actively monitors for reactions
- **Start:** 1 minute before scheduled news release
- **End:** 15 minutes after scheduled news release
- **Application:** Volatility detection only active during this window

### Maximum Trade Duration

- **Time limit:** 15 minutes from entry
- **Action:** Force close position at market price if still open after 15 minutes
- **Reason:** News trades are short-term momentum plays, not swing trades
- **Exceptions:** None (hard limit)

### High-Risk Mode Duration

- **Trigger:** Manual user activation before specific event
- **Auto-revert:** Immediately after first trade execution OR 5 minutes after news release (whichever comes first)
- **Cannot be:** Permanently enabled or set as default

---

## 10. BROKER-SPECIFIC ADJUSTMENTS

### Symbol Name Mapping (per broker)

**Example Configuration:**

```
Internal Symbol → Broker Symbol Mapping

EURUSD → "EURUSD" (most brokers)
EURUSD → "EURUSDm" (OANDA)
XAUUSD → "XAUUSD" (most brokers)
XAUUSD → "GOLD" (some brokers)
NAS100 → "NAS100" or "US100" or "USTEC"
```

**Implementation:** Broker-specific mapping stored in `/config/instruments.py`

### Pip Value Definitions (per asset)

| Asset  | Standard Lot | Pip Value (USD) | Notes                |
| ------ | ------------ | --------------- | -------------------- |
| EURUSD | 100,000      | $10             | Standard             |
| GBPUSD | 100,000      | $10             | Standard             |
| USDJPY | 100,000      | ~$9.17          | Varies with JPY rate |
| XAUUSD | 100 oz       | $10             | Per 0.10 move        |
| NAS100 | 1 contract   | $1              | Per 1.0 point        |
| US30   | 1 contract   | $1              | Per 1.0 point        |

---

## 11. LOGGING & AUDIT REQUIREMENTS

**Purpose:** Every decision must be explainable and reproducible

### Mandatory Log Fields (per decision)

- Timestamp (millisecond precision)
- Event name and scheduled time
- Risk mode (LOW or HIGH)
- Assets evaluated
- Volatility measurement
- Direction confirmation result
- Deviation from forecast (if HIGH_RISK)
- Risk calculations
- Entry/exit prices
- Spread at execution
- Position size
- Reason codes (trade / no-trade)

### Reason Codes (Examples)

```
TRADE_001: Volatility + direction confirmed (LOW_RISK)
TRADE_002: Deviation threshold met (HIGH_RISK)
NO_TRADE_001: Insufficient volatility
NO_TRADE_002: Direction not confirmed
NO_TRADE_003: Spread too wide
NO_TRADE_004: Daily loss limit reached
NO_TRADE_005: Consecutive loss limit reached
NO_TRADE_006: Deviation below threshold (HIGH_RISK abort)
```

---

## 12. RECOVERY & EDGE CASES

### System Startup

```
On startup:
1. Query MT5 for all open positions
2. Load internal state from last saved checkpoint
3. Reconcile: MT5 positions vs internal records
4. If mismatch → log error, apply MT5 state as truth
5. Apply exit rules to any open positions
```

### Connection Loss During Trade

```
If connection to MT5 is lost:
1. Attempt reconnection (max 3 attempts, 5 seconds apart)
2. If reconnection succeeds → reconcile positions
3. If reconnection fails → system pauses, alerts user
4. Manual intervention required before resuming
```

### Partial Fill

```
If order partially filled:
1. Calculate actual risk based on filled quantity
2. If within limits → accept partial fill
3. Cancel remaining order
4. Apply exit rules to filled position
```

### Slippage Threshold

```
max_acceptable_slippage = 3 pips (majors) / 5 pips (crosses) / 50 cents (gold)

If actual_fill - requested_price > max_acceptable_slippage:
    log_warning("High slippage detected")
    # But still accept the fill (trade already executed)
```

---

## 13. VALIDATION CHECKLIST

Before going live, verify these values are correctly implemented:

**Volatility:**

- [ ] 2.0× multiplier applied
- [ ] 60-minute lookback period
- [ ] 1-minute candles used

**Direction:**

- [ ] 50% threshold from reaction candle open
- [ ] Measured on next candle close

**Risk:**

- [ ] 1.0% LOW_RISK per trade
- [ ] 0.5% HIGH_RISK per trade
- [ ] 3.0% daily loss limit
- [ ] 3 consecutive loss limit

**Exits:**

- [ ] SL = 1.5× reaction range
- [ ] TP = 2.0× SL
- [ ] 15-minute time exit

**Multi-Asset:**

- [ ] Aggregate risk enforced
- [ ] Risk split correctly
- [ ] Max 3 assets per event

**Spreads:**

- [ ] 3× average calculated
- [ ] Absolute limits checked
- [ ] 60-minute averaging

**HIGH_RISK:**

- [ ] Deviation thresholds correct
- [ ] Auto-revert functional
- [ ] One-trade-only enforced

---

## 14. NOTES & ASSUMPTIONS

### What This Document Does NOT Cover

- Backtesting parameters (V2)
- Machine learning thresholds (V2+)
- Dynamic optimization (V2+)
- Multi-session trading (V2+)

### Known Limitations

- Thresholds are static (not adaptive to volatility regime)
- No intraday volatility scaling
- No correlation-adjusted position sizing
- No broker-specific latency compensation

### Why These Values

- **2.0× volatility:** Balance between sensitivity and noise
- **50% retrace:** Standard support/resistance concept
- **1.5× SL distance:** Allows normal retracement without premature stop
- **1:2 R:R:** Statistical minimum for profitable news trading
- **15-min exit:** News impact typically absorbed within this window
- **±0.3% CPI threshold:** Historically significant deviation level

---

## 15. DATA SOURCES & ACQUISITION

**Purpose:** Define exact data sources and acquisition methods for V1.0

### Primary Data Sources

#### 1. ForexFactory Calendar

**URL:** https://www.forexfactory.com/calendar  
**Method:** Web scraping (no official API)  
**Purpose:** Event scheduling and context

**Data Retrieved:**

- Event name (e.g., "US CPI m/m")
- Scheduled time (timezone: EST)
- Currency affected (USD, EUR, GBP, etc.)
- Impact level (high, medium, low)
- Forecast value
- Previous value
- Actual value (post-release)

**Update Frequency:**

- Check every 60 minutes for upcoming events
- Scrape 30 minutes before high-impact events
- Re-check actual values 2 minutes after scheduled time

**Rate Limiting:**

- Maximum 1 request per minute
- Implement 5-second delay between retries
- User-Agent: "NewsBot/1.0 (Educational Trading System)"

**Error Handling:**

```
If ForexFactory unreachable:
- Log error with timestamp
- Retry 3 times (5-second intervals)
- If still failing → system enters PAUSE state
- Alert user to manual intervention
```

**Filtering Rules:**

- Only scrape "high impact" events
- Only currencies in allowed_events.py
- Ignore preliminary/revised releases (use final only)

---

#### 2. Government / Central Bank Sites

**Method:** Web scraping or RSS feeds  
**Purpose:** Ground truth for actual released values (especially HIGH_RISK mode)

**Sources by Region:**

| Region       | Source                                      | Events Covered          | Method       |
| ------------ | ------------------------------------------- | ----------------------- | ------------ |
| **USA**      | Bureau of Labor Statistics (bls.gov)        | CPI, NFP, Unemployment  | Scraping     |
| **USA**      | Federal Reserve (federalreserve.gov)        | Interest Rate Decisions | RSS/Scraping |
| **UK**       | Office for National Statistics (ons.gov.uk) | CPI, GDP, Employment    | Scraping     |
| **Eurozone** | Eurostat (ec.europa.eu/eurostat)            | CPI, GDP                | Scraping     |

**When to Use:**

- HIGH_RISK mode always attempts government source first
- If government source fails → fallback to ForexFactory
- LOW_RISK mode uses ForexFactory (speed not critical)

**Rate Limiting:**

- Maximum 1 request per 30 seconds per domain
- Cache results for 24 hours (data doesn't change)

**Error Handling:**

```
If government site unreachable:
- Log warning (not critical)
- Immediately fallback to ForexFactory
- Do NOT block trade execution
```

---

#### 3. MetaTrader 5 Platform (Price Data)

**Library:** `MetaTrader5` (official) or `silicon-metatrader5` (macOS dev)  
**Purpose:** Real-time price data, historical candles, account info

**Data Retrieved:**

- 1-minute OHLC candles (last 60 minutes)
- Current bid/ask prices
- Current spread
- Account balance
- Open positions
- Symbol information (pip size, lot size, etc.)

**Update Frequency:**

- Historical candles: Fetched once at start of news window
- Current prices: Polled every 1 second during news window
- Spread monitoring: Continuous during news window

**Critical Requirements:**

- Connection must be verified before every trade
- Position reconciliation on startup (MT5 is source of truth)
- All network calls must have 10-second timeout

**Error Handling:**

```
If MT5 connection lost:
- Attempt reconnection (3 attempts, 5 seconds apart)
- If reconnection succeeds → reconcile positions
- If reconnection fails → EMERGENCY PAUSE
- Do NOT attempt new trades until connection restored
```

---

#### 4. Free APIs (Optional - V1.0)

**Status:** Optional for V1.0, use only if implementation is trivial

**Approved APIs:**

- Alpha Vantage (free tier: 5 calls/minute)
- FRED API (Federal Reserve Economic Data - unlimited)

**Do NOT use unless:**

- You have validated the free tier limits
- Implementation takes < 1 hour
- Data quality is verified

**If API fails:**

- Fallback to scraping immediately
- Never block system operation

---

### Data Flow Architecture

```
News Event Detected (ForexFactory)
        ↓
Is HIGH_RISK mode enabled?
   ├─ YES → Try government site for actual value
   │         ├─ Success → Use official value
   │         └─ Fail → Fallback to ForexFactory
   │
   └─ NO → Use ForexFactory actual value
        ↓
Fetch MT5 Price Data (last 60min + current)
        ↓
Calculate Volatility (Section 1)
        ↓
Confirm Direction (Section 2)
        ↓
Execute Trade (if approved)
```

---

### Data Quality Validation

All scraped data must pass validation before use:

**ForexFactory Events:**

```python
def validate_event(event: dict) -> bool:
    required_fields = ['name', 'time', 'currency', 'impact', 'forecast']
    return all(field in event for field in required_fields)
```

**Price Data:**

```python
def validate_candles(candles: list) -> bool:
    return (
        len(candles) >= 60 and  # Full hour of data
        all(c['high'] >= c['low'] for c in candles) and  # Valid OHLC
        all(c['close'] > 0 for c in candles)  # No zero prices
    )
```

**Actual Values:**

```python
def validate_actual(actual: float, forecast: float) -> bool:
    return (
        actual is not None and
        abs(actual) < abs(forecast) * 10  # Sanity check (not 10x forecast)
    )
```

---

### Caching Strategy

To minimize network requests:

**ForexFactory Calendar:**

- Cache for 30 minutes
- Invalidate 5 minutes before high-impact events

**Government Sites:**

- Cache for 24 hours (data is historical, doesn't change)

**MT5 Price Data:**

- Never cache (must be real-time)

**Implementation:**

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=128)
def get_calendar_cached(date: str) -> list:
    return scrape_forexfactory(date)
```

---

### Scraping Ethics & Legal

**User-Agent Header:**
All scrapers must identify themselves:

```
User-Agent: NewsBot/1.0 (Educational Automated Trading System; Contact: your-email@example.com)
```

**Robots.txt Compliance:**

- Check robots.txt before scraping
- Respect crawl-delay directives
- Do not scrape if explicitly forbidden

**Terms of Service:**

- ForexFactory: Educational use allowed, no commercial resale
- Government sites: Public data, unrestricted use
- Always verify current TOS before deployment

**Rate Limiting:**

- Never make more than 1 request per minute to any single domain
- Implement exponential backoff on errors
- Cache aggressively to minimize requests

---

### Failure Scenarios & Actions

| Failure              | Action               | System State |
| -------------------- | -------------------- | ------------ |
| ForexFactory down    | Retry 3x → PAUSE     | No trading   |
| Government site down | Use ForexFactory     | Continue     |
| MT5 disconnected     | Reconnect 3x → PAUSE | No trading   |
| Invalid data format  | Log + skip event     | Continue     |
| Network timeout      | Retry with backoff   | Continue     |
| All sources failing  | EMERGENCY STOP       | Alert user   |

---

### Implementation Dependencies

**Required Python Libraries:**

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
MetaTrader5>=5.0.45 (or silicon-metatrader5 for macOS)
```

**Optional Libraries:**

```
selenium>=4.15.0  # Only if JavaScript rendering needed
feedparser>=6.0.10  # For RSS feeds
```

---

### Testing Requirements

Before going live, verify:

- [ ] ForexFactory scraper retrieves correct event times
- [ ] Forecast/previous values parse correctly
- [ ] Government site scraper handles missing data
- [ ] MT5 connection recovery works
- [ ] Rate limiting prevents DOS
- [ ] Cache reduces redundant requests
- [ ] All validation functions reject bad data
- [ ] Failure scenarios trigger correct actions

---

## VERSION HISTORY

**V1.0 (Current - 2025-12-30)**

- Initial implementation-ready specification
- All thresholds defined
- Multi-asset support included (disabled by default)
- Data sources and acquisition methods specified (Section 15)

**Future (V1.1+)**

- Adaptive volatility thresholds
- Broker-specific latency tables
- Event-specific R:R ratios
- Additional data source integrations

---

**END OF DOCUMENT**
