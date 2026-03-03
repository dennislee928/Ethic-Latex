# SheetJS (xlsx) - Quick API Reference

**Package**: `xlsx` | **Version**: 0.18.5+ | **Docs**: https://docs.sheetjs.com

## Installation

```bash
npm install xlsx
```

## Core Import

```typescript
import * as XLSX from 'xlsx';
```

## Workbook Creation

```typescript
const wb = XLSX.utils.book_new();
```

## Sheet from Array of Arrays

```typescript
const data = [
  ['Name', 'Age', 'City'],      // Header row
  ['Alice', 30, 'New York'],
  ['Bob', 25, 'London'],
];

const ws = XLSX.utils.aoa_to_sheet(data);
XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
```

## Sheet from JSON

```typescript
const jsonData = [
  { name: 'Alice', age: 30, city: 'New York' },
  { name: 'Bob', age: 25, city: 'London' },
];

const ws = XLSX.utils.json_to_sheet(jsonData);
XLSX.utils.book_append_sheet(wb, ws, 'Employees');
```

## Formulas

```typescript
const data = [
  ['Item', 'Qty', 'Price', 'Total'],
  ['Widget', 10, 5, { f: 'B2*C2' }],           // Formula: =B2*C2
  ['Gadget', 5, 12, { f: 'B3*C3' }],
  ['', '', 'Sum:', { f: 'SUM(D2:D3)' }],       // Formula: =SUM(D2:D3)
];

const ws = XLSX.utils.aoa_to_sheet(data);
```

**Note**: Formulas are written to file but calculated when opened in Excel/Sheets.

## Cross-Sheet References

```typescript
// Reference another sheet in formula
{ f: 'Sheet2!A1' }           // Single cell
{ f: "SUM(Sheet2!A1:A10)" }  // Range
{ f: "Details!D7" }          // Named sheet
```

## Column Widths

```typescript
ws['!cols'] = [
  { wch: 20 },  // Column A: 20 characters wide
  { wch: 10 },  // Column B: 10 characters wide
  { wch: 15 },  // Column C: 15 characters wide
];
```

## Merge Cells

```typescript
ws['!merges'] = [
  { s: { r: 0, c: 0 }, e: { r: 0, c: 3 } },  // Merge A1:D1
  // s = start (row, col), e = end (row, col)
  // r = row (0-indexed), c = column (0-indexed)
];
```

## Row Heights

```typescript
ws['!rows'] = [
  { hpt: 30 },  // Row 1: 30 points tall
  { hpt: 20 },  // Row 2: 20 points tall
];
```

## Add Data to Existing Sheet

```typescript
// Append at specific origin
XLSX.utils.sheet_add_aoa(ws, newData, { origin: 'A5' });

// Append at next empty row
const range = XLSX.utils.decode_range(ws['!ref'] || 'A1');
const startRow = range.e.r + 1;
XLSX.utils.sheet_add_aoa(ws, newData, { origin: startRow });
```

## Read Existing Workbook

```typescript
// From file (Node.js)
const wb = XLSX.readFile('input.xlsx');

// From buffer
const wb = XLSX.read(buffer, { type: 'buffer' });

// From base64
const wb = XLSX.read(base64String, { type: 'base64' });
```

## Get Sheet Data

```typescript
// Sheet names
const sheetNames = wb.SheetNames;  // ['Sheet1', 'Sheet2']

// Get sheet by name
const ws = wb.Sheets['Sheet1'];

// Convert to JSON
const data = XLSX.utils.sheet_to_json(ws);

// Convert to array of arrays
const aoa = XLSX.utils.sheet_to_json(ws, { header: 1 });

// Convert to CSV
const csv = XLSX.utils.sheet_to_csv(ws);
```

## Export

```typescript
// Node.js - save to file
XLSX.writeFile(wb, 'output.xlsx');

// Get as Buffer (Node.js / Workers)
const buffer = XLSX.write(wb, { type: 'buffer', bookType: 'xlsx' });

// HTTP Response (Cloudflare Workers)
const buffer = XLSX.write(wb, { type: 'buffer', bookType: 'xlsx' });
return new Response(buffer, {
  headers: {
    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'Content-Disposition': 'attachment; filename="spreadsheet.xlsx"',
  },
});

// Get as base64 (Browser)
const b64 = XLSX.write(wb, { type: 'base64', bookType: 'xlsx' });

// Get as binary string
const bstr = XLSX.write(wb, { type: 'binary', bookType: 'xlsx' });
```

## Book Types

| Type | Extension | Description |
|------|-----------|-------------|
| `xlsx` | .xlsx | Excel 2007+ XML |
| `xlsm` | .xlsm | Excel with macros |
| `xlsb` | .xlsb | Excel binary |
| `xls` | .xls | Excel 97-2004 |
| `csv` | .csv | Comma-separated |
| `txt` | .txt | Tab-separated |
| `html` | .html | HTML table |

## Cell Reference Utilities

```typescript
// Encode cell address
XLSX.utils.encode_cell({ r: 0, c: 0 });  // 'A1'
XLSX.utils.encode_cell({ r: 1, c: 2 });  // 'C2'

// Decode cell address
XLSX.utils.decode_cell('A1');  // { r: 0, c: 0 }
XLSX.utils.decode_cell('C2');  // { r: 1, c: 2 }

// Encode range
XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: 5, c: 3 } });  // 'A1:D6'

// Decode range
XLSX.utils.decode_range('A1:D6');
```

## Direct Cell Access

```typescript
// Read cell
const cell = ws['A1'];
console.log(cell.v);  // Value
console.log(cell.f);  // Formula (if any)

// Write cell directly
ws['E1'] = { v: 'Hello', t: 's' };  // t: 's' = string
ws['E2'] = { v: 42, t: 'n' };       // t: 'n' = number
ws['E3'] = { f: 'SUM(A1:A10)' };    // Formula

// Update range after direct cell access
ws['!ref'] = 'A1:E10';  // Must include all cells
```

## Cell Types

| Type | Code | Description |
|------|------|-------------|
| String | `s` | Text value |
| Number | `n` | Numeric value |
| Boolean | `b` | true/false |
| Date | `d` | Date object |
| Error | `e` | Error value |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Formula without quotes in JSON | Use object: `{ f: 'SUM(A:A)' }` |
| Forgetting to update `!ref` | Always update after direct cell access |
| Column index 1-based | Columns are 0-indexed (A=0, B=1) |
| Row index 1-based | Rows are 0-indexed (1=0, 2=1) |
