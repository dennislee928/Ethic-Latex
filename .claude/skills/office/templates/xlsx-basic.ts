/**
 * XLSX Basic Template - Excel Spreadsheet Generation
 *
 * Creates a workbook with:
 * - Multiple sheets
 * - Data from arrays and JSON
 * - Formulas
 * - Column widths
 *
 * Works in: Node.js, Cloudflare Workers, Browser
 *
 * Usage:
 *   npm install xlsx
 *   npx tsx xlsx-basic.ts
 */

import * as XLSX from 'xlsx';
import { writeFileSync } from 'fs';

// =============================================================================
// WORKBOOK CREATION
// =============================================================================

function createWorkbook(): XLSX.WorkBook {
  const wb = XLSX.utils.book_new();

  // -------------------------------------------------------------------------
  // SHEET 1: Summary (from array of arrays)
  // -------------------------------------------------------------------------
  const summaryData = [
    ['Monthly Sales Summary'],
    [''],
    ['Metric', 'Value'],
    ['Total Revenue', { f: 'Details!D7' }], // Formula referencing other sheet
    ['Total Units', { f: 'Details!C7' }],
    ['Average Price', { f: 'Details!D7/Details!C7' }],
    [''],
    ['Report Date', new Date().toISOString().split('T')[0]],
  ];

  const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);

  // Set column widths
  summarySheet['!cols'] = [
    { wch: 20 }, // Column A
    { wch: 15 }, // Column B
  ];

  // Merge cells for title (A1:B1)
  summarySheet['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 1 } }];

  XLSX.utils.book_append_sheet(wb, summarySheet, 'Summary');

  // -------------------------------------------------------------------------
  // SHEET 2: Details (from array of arrays with formulas)
  // -------------------------------------------------------------------------
  const detailsData = [
    ['Product', 'Category', 'Units Sold', 'Revenue'],
    ['Widget A', 'Electronics', 150, 4500],
    ['Widget B', 'Electronics', 200, 5000],
    ['Gadget X', 'Accessories', 75, 1875],
    ['Gadget Y', 'Accessories', 120, 2400],
    ['Service Z', 'Services', 50, 2500],
    ['TOTAL', '', { f: 'SUM(C2:C6)' }, { f: 'SUM(D2:D6)' }],
  ];

  const detailsSheet = XLSX.utils.aoa_to_sheet(detailsData);

  // Set column widths
  detailsSheet['!cols'] = [
    { wch: 15 }, // Product
    { wch: 15 }, // Category
    { wch: 12 }, // Units
    { wch: 12 }, // Revenue
  ];

  XLSX.utils.book_append_sheet(wb, detailsSheet, 'Details');

  // -------------------------------------------------------------------------
  // SHEET 3: From JSON data
  // -------------------------------------------------------------------------
  const jsonData = [
    { id: 1, name: 'Alice', department: 'Sales', salary: 75000 },
    { id: 2, name: 'Bob', department: 'Engineering', salary: 95000 },
    { id: 3, name: 'Carol', department: 'Marketing', salary: 70000 },
    { id: 4, name: 'David', department: 'Engineering', salary: 90000 },
    { id: 5, name: 'Eve', department: 'Sales', salary: 72000 },
  ];

  const employeesSheet = XLSX.utils.json_to_sheet(jsonData);

  // Set column widths
  employeesSheet['!cols'] = [
    { wch: 5 }, // id
    { wch: 15 }, // name
    { wch: 15 }, // department
    { wch: 12 }, // salary
  ];

  XLSX.utils.book_append_sheet(wb, employeesSheet, 'Employees');

  return wb;
}

// =============================================================================
// EXPORT FUNCTIONS
// =============================================================================

/**
 * Save to file (Node.js only)
 */
function saveToFile(wb: XLSX.WorkBook, filename: string) {
  XLSX.writeFile(wb, filename);
  console.log(`✅ Saved: ${filename}`);
}

/**
 * Get as Buffer (Cloudflare Workers / Node.js)
 */
function toBuffer(wb: XLSX.WorkBook): Buffer {
  return XLSX.write(wb, { type: 'buffer', bookType: 'xlsx' }) as Buffer;
}

/**
 * Get as Response (Cloudflare Workers)
 */
function toResponse(wb: XLSX.WorkBook, filename: string): Response {
  const buffer = toBuffer(wb);
  return new Response(buffer, {
    headers: {
      'Content-Type':
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  });
}

/**
 * Get as base64 (Browser download)
 */
function toBase64(wb: XLSX.WorkBook): string {
  return XLSX.write(wb, { type: 'base64', bookType: 'xlsx' });
}

// =============================================================================
// UTILITY: Add data to existing sheet
// =============================================================================

function appendDataToSheet(
  wb: XLSX.WorkBook,
  sheetName: string,
  newData: unknown[][]
) {
  const ws = wb.Sheets[sheetName];
  if (!ws) throw new Error(`Sheet "${sheetName}" not found`);

  // Find the next empty row
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1');
  const startRow = range.e.r + 1;

  // Add new data
  XLSX.utils.sheet_add_aoa(ws, newData, { origin: startRow });
}

// =============================================================================
// UTILITY: Read existing workbook
// =============================================================================

function readWorkbook(filename: string): XLSX.WorkBook {
  return XLSX.readFile(filename);
}

function sheetToJson<T>(wb: XLSX.WorkBook, sheetName: string): T[] {
  const ws = wb.Sheets[sheetName];
  if (!ws) throw new Error(`Sheet "${sheetName}" not found`);
  return XLSX.utils.sheet_to_json(ws);
}

// =============================================================================
// MAIN
// =============================================================================

function main() {
  console.log('Creating Excel workbook...');

  const wb = createWorkbook();
  saveToFile(wb, 'report.xlsx');

  console.log('Done! Open report.xlsx to view.');
  console.log('Note: Formulas will calculate when opened in Excel.');
}

// Run if executed directly
main();

// Export for use as module
export {
  createWorkbook,
  saveToFile,
  toBuffer,
  toResponse,
  toBase64,
  appendDataToSheet,
  readWorkbook,
  sheetToJson,
};
