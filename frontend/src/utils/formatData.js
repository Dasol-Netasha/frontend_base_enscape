/**
 * 날짜/시간 값을 'YYYY-MM-DD HH:mm:ss' 형식으로 포맷하는 유틸리티.
 *
 * 사용 예:
 *   formatData('2024-03-01T09:30:00Z')          // → '2024-03-01 09:30:00'
 *   formatData(null)                              // → '-'
 *   formatData('이상한값', { type: 'datetime' }) // → '이상한값' (파싱 실패 시 원본 반환)
 */

/**
 * ISO 문자열, Date 객체 등 날짜 값 → 'YYYY-MM-DD HH:mm:ss' 변환.
 * 값이 없거나 파싱 실패 시 안전한 대체값을 반환한다.
 *
 * @param {*} value - 변환할 날짜 값 (ISO 문자열, timestamp 숫자 등)
 * @param {string} locale - 현재 미사용 (향후 locale 기반 포맷 확장용)
 * @returns {string}
 */
export const formatDateTime = (value, locale = 'ko-KR') => {
  if (value === null || value === undefined || value === '') {
    return '-'  // 빈 값이면 대시 표시
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return String(value)  // 파싱 실패 시 원본 문자열 그대로 반환
  }

  // 각 단위를 2자리 0패딩으로 맞춘다
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

/**
 * 테이블 셀 값을 type에 따라 적절히 포맷한다.
 * 현재 지원 type: 'datetime' (기본값)
 * 값이 null/undefined이면 '-'를 반환한다.
 *
 * @param {*} value - 포맷할 값
 * @param {{ type?: string, locale?: string }} options
 * @returns {string|*}
 */
export const formatData = (value, options = {}) => {
  const { type = 'datetime', locale = 'ko-KR' } = options

  if (type === 'datetime') {
    return formatDateTime(value, locale)
  }

  // 알 수 없는 type이면 값 그대로 반환, null/undefined는 '-'
  return value ?? '-'
}

/**
 * 숫자 값을 표시용 문자열로 변환한다.
 * maximumFractionDigits 만큼만 소수 자릿수를 표현하며, 그 범위에서 반올림한다.
 *
 * @param {*} value
 * @param {number} maximumFractionDigits
 * @param {string} fallback
 * @param {string} locale
 * @returns {string}
 */
export const formatNumber = (
  value,
  maximumFractionDigits = 0,
  fallback = '-',
  locale = 'ko-KR',
) => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return fallback
  }

  return numeric.toLocaleString(locale, {
    minimumFractionDigits: 0,
    maximumFractionDigits,
  })
}