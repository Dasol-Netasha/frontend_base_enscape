import * as XLSX from 'xlsx'

/**
 * 테이블 데이터를 CSV 또는 Excel(.xlsx) 형식으로 다운로드하는 유틸리티
 *
 * @param {Array<{key: string, label: string}>} columns - 컬럼 정의
 * @param {Array<Object>} rows - 데이터 행 배열
 * @param {string} filename - 확장자 제외 파일명
 */

function escapeCell(value) {
  if (value === null || value === undefined) return ''
  const str = String(value)
  // CSV injection 방지: 수식 시작 문자 앞에 탭 추가
  if (['+', '-', '=', '@', '\t', '\r'].includes(str[0])) {
    return `"\t${str.replace(/"/g, '""')}"`
  }
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

/**
 * CSV 다운로드
 */
export function downloadCSV(columns, rows, filename = 'data') {
  const header = columns.map((c) => escapeCell(c.label)).join(',')
  const body = rows.map((row) => columns.map((c) => escapeCell(row[c.key])).join(','))
  const csv = [header, ...body].join('\r\n')

  // BOM 추가 (Excel에서 한글 깨짐 방지)
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  triggerDownload(blob, `${filename}.csv`)
}

/**
 * Excel(.xlsx) 다운로드
 */
export function downloadExcel(columns, rows, filename = 'data') {
  const worksheetRows = [
    columns.map((column) => column.label),
    ...rows.map((row) => columns.map((column) => row?.[column.key] ?? '')),
  ]

  const worksheet = XLSX.utils.aoa_to_sheet(worksheetRows)
  const workbook = XLSX.utils.book_new()

  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
  XLSX.writeFile(workbook, `${filename}.xlsx`)
}

/**
 * Blob 객체를 브라우저 다운로드로 트리거한다.
 * - 임시 <a> 태그를 생성해 클릭 후 즉시 제거하는 표준 패턴.
 * - createObjectURL로 만든 URL은 메모리 누수 방지를 위해 반드시 revoke.
 */
function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob)  // Blob을 가리키는 임시 URL 생성
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()                              // 클릭 이벤트로 다운로드 시작
  document.body.removeChild(a)          // 사용 후 DOM에서 제거
  URL.revokeObjectURL(url)              // 임시 URL 해제 (메모리 반환)
}
