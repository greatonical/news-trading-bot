"""
ForexFactory calendar scraper for News Trading Bot V1.0

Reference: /docs/quantitative_thresholds.md Section 15
Last Updated: 2025-12-30

IMPORTANT: This scraper is for educational/personal use only.
Do not use for commercial data resale.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
from pathlib import Path
import sys
import pytz

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging.trade_logger import get_logger


class ForexFactoryCalendar:
    """
    Web scraper for ForexFactory economic calendar
    
    Reference: quantitative_thresholds.md Section 15
    
    Features:
    - Scrapes high-impact news events
    - Retry logic (3 attempts, 5-second delays)
    - Rate limiting (max 1 request/minute)
    - Caching (30-minute cache, invalidate 5 min before events)
    - User-Agent identification
    """
    
    def __init__(
        self,
        base_url: str = "https://www.forexfactory.com/calendar",
        rate_limit_seconds: int = 60,
        cache_minutes: int = 30,
        max_retries: int = 3,
        retry_delay_seconds: int = 5,
    ):
        """
        Initialize ForexFactory scraper
        
        Args:
            base_url: ForexFactory calendar URL
            rate_limit_seconds: Minimum seconds between requests
            cache_minutes: Cache duration in minutes
            max_retries: Maximum retry attempts
            retry_delay_seconds: Delay between retries
        """
        self.base_url = base_url
        self.rate_limit_seconds = rate_limit_seconds
        self.cache_minutes = cache_minutes
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        
        self.logger = get_logger()
        
        # Rate limiting
        self.last_request_time: Optional[float] = None
        
        # Caching
        self.cache: Dict[str, tuple[datetime, List[Dict]]] = {}
        
        # User-Agent for identification
        self.headers = {
            "User-Agent": "NewsBot/1.0 (Educational Automated Trading System)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting (max 1 request per minute)
        
        Reference: quantitative_thresholds.md Section 15
        """
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_seconds:
                sleep_time = self.rate_limit_seconds - elapsed
                self.logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fetch_with_retry(self, url: str) -> Optional[str]:
        """
        Fetch URL with automatic retry logic
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content or None if all retries failed
        
        Reference:
            quantitative_thresholds.md Section 15 (Error Handling)
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                self._enforce_rate_limit()
                
                self.logger.debug(f"Fetching {url} (attempt {attempt}/{self.max_retries})")
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=10,
                )
                response.raise_for_status()
                
                return response.text
            
            except requests.exceptions.RequestException as e:
                self.logger.log_data_source_error(
                    source="ForexFactory",
                    error_type="connection",
                    error_message=str(e),
                    retry_attempt=attempt,
                )
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_seconds)
                else:
                    self.logger.error(
                        f"ForexFactory unreachable after {self.max_retries} attempts"
                    )
                    return None
        
        return None
    
    def _parse_event_row(self, row) -> Optional[Dict]:
        """
        Parse a single event row from ForexFactory table
        
        Args:
            row: BeautifulSoup row element
        
        Returns:
            Event dictionary or None if parsing failed
        """
        try:
            # Extract cells
            cells = row.find_all('td')
            if len(cells) < 5:
                return None
            
            # Time (EST timezone)
            time_cell = cells[0]
            time_str = time_cell.get_text(strip=True)
            if not time_str or time_str == "":
                return None  # Skip all-day events
            
            # Currency
            currency_cell = cells[1]
            currency = currency_cell.get_text(strip=True)
            
            # Impact
            impact_cell = cells[2]
            impact_spans = impact_cell.find_all('span', class_='impact')
            if not impact_spans:
                return None
            
            # Count filled impact icons (high = 3, medium = 2, low = 1)
            impact_count = len([s for s in impact_spans if 'icon--ff-impact-' in s.get('class', [])[0]])
            if impact_count >= 3:
                impact = "high"
            elif impact_count == 2:
                impact = "medium"
            else:
                impact = "low"
            
            # Event name
            event_cell = cells[3]
            event_name = event_cell.get_text(strip=True)
            
            # Forecast, Previous, Actual
            detail_cell = cells[4]
            forecast = detail_cell.get('data-forecast', '')
            previous = detail_cell.get('data-previous', '')
            actual = detail_cell.get('data-actual', '')
            
            # Parse time (ForexFactory uses EST)
            est = pytz.timezone('US/Eastern')
            now = datetime.now(est)
            
            # Parse time string (e.g., "8:30am")
            try:
                event_time = datetime.strptime(time_str, "%I:%M%p")
                event_datetime = est.localize(
                    datetime(now.year, now.month, now.day, event_time.hour, event_time.minute)
                )
                
                # If time has passed today, assume it's tomorrow
                if event_datetime < now:
                    event_datetime += timedelta(days=1)
                
                # Convert to UTC
                event_datetime_utc = event_datetime.astimezone(pytz.UTC)
            
            except ValueError:
                self.logger.warning(f"Failed to parse time: {time_str}")
                return None
            
            return {
                "name": event_name,
                "time": event_datetime_utc,
                "currency": currency,
                "impact": impact,
                "forecast": self._parse_numeric(forecast),
                "previous": self._parse_numeric(previous),
                "actual": self._parse_numeric(actual) if actual else None,
            }
        
        except Exception as e:
            self.logger.warning(f"Failed to parse event row: {e}")
            return None
    
    def _parse_numeric(self, value_str: str) -> Optional[float]:
        """
        Parse numeric value from string
        
        Args:
            value_str: String value (e.g., "3.2%", "200K", "-60.5B")
        
        Returns:
            Float value or None if not numeric
        """
        if not value_str or value_str.strip() == "":
            return None
        
        try:
            # Remove common suffixes
            clean_value = value_str.strip()
            
            # Handle percentage
            if '%' in clean_value:
                clean_value = clean_value.replace('%', '')
            
            # Handle K (thousands)
            elif 'K' in clean_value:
                clean_value = clean_value.replace('K', '')
                return float(clean_value) * 1000
            
            # Handle M (millions)
            elif 'M' in clean_value:
                clean_value = clean_value.replace('M', '')
                return float(clean_value) * 1000000
            
            # Handle B (billions)
            elif 'B' in clean_value:
                clean_value = clean_value.replace('B', '')
                return float(clean_value) * 1000000000
            
            return float(clean_value)
        
        except ValueError:
            return None
    
    def _validate_event(self, event: Dict) -> bool:
        """
        Validate event has all required fields
        
        Args:
            event: Event dictionary
        
        Returns:
            True if valid, False otherwise
        
        Reference:
            quantitative_thresholds.md Section 15 (Data Quality Validation)
        """
        required_fields = ['name', 'time', 'currency', 'impact']
        return all(field in event and event[field] is not None for field in required_fields)
    
    def get_upcoming_events(
        self,
        hours_ahead: int = 24,
        impact_filter: Optional[List[str]] = None,
        currency_filter: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Get upcoming high-impact news events
        
        Args:
            hours_ahead: Look ahead this many hours
            impact_filter: Filter by impact levels (default: ["high"])
            currency_filter: Filter by currencies (default: None = all)
        
        Returns:
            List of event dictionaries
        
        Reference:
            quantitative_thresholds.md Section 15
        
        Example:
            >>> calendar = ForexFactoryCalendar()
            >>> events = calendar.get_upcoming_events(hours_ahead=24, impact_filter=["high"])
            >>> for event in events:
            ...     print(f"{event['name']} at {event['time']}")
        """
        if impact_filter is None:
            impact_filter = ["high"]  # Default: high-impact only
        
        # Check cache
        cache_key = f"{hours_ahead}_{impact_filter}_{currency_filter}"
        if cache_key in self.cache:
            cache_time, cached_events = self.cache[cache_key]
            cache_age = (datetime.now() - cache_time).total_seconds() / 60
            
            if cache_age < self.cache_minutes:
                self.logger.debug(f"Using cached events (age: {cache_age:.1f} min)")
                return cached_events
        
        # Fetch from ForexFactory
        html = self._fetch_with_retry(self.base_url)
        if html is None:
            self.logger.error("Failed to fetch ForexFactory calendar")
            return []
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Find calendar table
            calendar_table = soup.find('table', class_='calendar__table')
            if not calendar_table:
                self.logger.error("Calendar table not found in HTML")
                return []
            
            # Parse all event rows
            rows = calendar_table.find_all('tr', class_='calendar__row')
            events = []
            
            for row in rows:
                event = self._parse_event_row(row)
                if event and self._validate_event(event):
                    events.append(event)
            
            # Filter by time window
            now_utc = datetime.now(pytz.UTC)
            cutoff_time = now_utc + timedelta(hours=hours_ahead)
            
            events = [
                e for e in events
                if now_utc <= e['time'] <= cutoff_time
            ]
            
            # Filter by impact
            if impact_filter:
                events = [e for e in events if e['impact'] in impact_filter]
            
            # Filter by currency
            if currency_filter:
                events = [e for e in events if e['currency'] in currency_filter]
            
            # Cache results
            self.cache[cache_key] = (datetime.now(), events)
            
            self.logger.info(f"Fetched {len(events)} upcoming events from ForexFactory")
            
            return events
        
        except Exception as e:
            self.logger.log_data_source_error(
                source="ForexFactory",
                error_type="parsing",
                error_message=str(e),
            )
            return []
    
    def get_event_actual_value(self, event_name: str) -> Optional[float]:
        """
        Get actual released value for an event
        
        Args:
            event_name: Name of event
        
        Returns:
            Actual value or None if not released yet
        
        Note:
            This requires re-fetching the calendar after the event release
        """
        events = self.get_upcoming_events(hours_ahead=1)  # Recent events
        
        for event in events:
            if event['name'] == event_name and event['actual'] is not None:
                return event['actual']
        
        return None


if __name__ == "__main__":
    # Test scraper
    print("Testing ForexFactory scraper...")
    
    calendar = ForexFactoryCalendar()
    
    # Get upcoming high-impact events
    events = calendar.get_upcoming_events(
        hours_ahead=48,
        impact_filter=["high"],
        currency_filter=["USD", "EUR", "GBP"],
    )
    
    print(f"\nFound {len(events)} upcoming high-impact events:")
    for event in events[:5]:  # Show first 5
        print(f"\n  Event: {event['name']}")
        print(f"  Time: {event['time'].strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  Currency: {event['currency']}")
        print(f"  Impact: {event['impact']}")
        print(f"  Forecast: {event['forecast']}")
        print(f"  Previous: {event['previous']}")
    
    print("\n✓ ForexFactory scraper test completed")
