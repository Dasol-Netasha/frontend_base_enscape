export const parseBilingualLabel = (rawLabel) => {
  const text = String(rawLabel ?? '').trim()
  if (!text) {
    return { display: '', tooltip: '' }
  }

  if (!text.endsWith(')')) {
    return { display: text, tooltip: '' }
  }

  let depth = 0
  let openingIndex = -1

  for (let index = text.length - 1; index >= 0; index -= 1) {
    const ch = text[index]
    if (ch === ')') {
      depth += 1
      continue
    }
    if (ch === '(') {
      depth -= 1
      if (depth === 0) {
        openingIndex = index
        break
      }
    }
  }

  if (openingIndex <= 0) {
    return { display: text, tooltip: '' }
  }

  const display = text.slice(0, openingIndex).trim()
  const tooltip = text.slice(openingIndex + 1, -1).trim()
  if (!display || !tooltip) {
    return { display: text, tooltip: '' }
  }

  return { display, tooltip }
}
