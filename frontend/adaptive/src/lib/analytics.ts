const SESSION_KEY = 'ir-anthology-analytics-session';
const ENABLED_KEY = 'ir-anthology-analytics-enabled';
const NOTICE_KEY = 'ir-anthology-analytics-notice-dismissed';

function browserStorage(kind: 'localStorage' | 'sessionStorage'): Storage | null {
  if (typeof window === 'undefined') return null;
  try {
    return window[kind];
  } catch {
    return null;
  }
}

export function getAnalyticsSessionId(): string {
  const storage = browserStorage('sessionStorage');
  const existing = storage?.getItem(SESSION_KEY);
  if (existing) return existing;

  const id = crypto.randomUUID();
  storage?.setItem(SESSION_KEY, id);
  return id;
}

export function isAnalyticsEnabled(): boolean {
  return browserStorage('localStorage')?.getItem(ENABLED_KEY) !== 'false';
}

export function setAnalyticsEnabled(enabled: boolean): void {
  browserStorage('localStorage')?.setItem(ENABLED_KEY, String(enabled));
}

export function isPrivacyNoticeDismissed(): boolean {
  return browserStorage('localStorage')?.getItem(NOTICE_KEY) === 'true';
}

export function dismissPrivacyNotice(): void {
  browserStorage('localStorage')?.setItem(NOTICE_KEY, 'true');
}

export function analyticsHeaders(): Record<string, string> {
  return {
    'X-Analytics-Enabled': String(isAnalyticsEnabled()),
    'X-Session-Id': getAnalyticsSessionId()
  };
}
