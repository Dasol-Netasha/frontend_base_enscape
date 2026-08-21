const readCssVar = (name, fallback) => {
  if (typeof window === 'undefined') {
    return fallback
  }

  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return value || fallback
}

export const getChartThemeTokens = () => {
  return {
    textStrong: readCssVar('--theme-text-strong', '#0f172a'),
    textBody: readCssVar('--theme-text-body', '#334155'),
    textSubtle: readCssVar('--theme-text-subtle', '#64748b'),
    borderSoft: readCssVar('--theme-border-soft', '#e2e8f0'),
    surface1: readCssVar('--theme-surface-1', '#ffffff'),
    surface2: readCssVar('--theme-surface-2', '#f8fafc'),
    surface3: readCssVar('--theme-surface-3', '#f1f5f9'),
    accent: readCssVar('--theme-main-accent', '#0369a1'),
  }
}