/**
 * PDF Basic Template - PDF Generation
 *
 * Creates a PDF with:
 * - Text with custom fonts
 * - Images
 * - Shapes and lines
 * - Multiple pages
 *
 * Works in: Node.js, Cloudflare Workers, Browser
 *
 * Usage:
 *   npm install pdf-lib
 *   npx tsx pdf-basic.ts
 */

import { PDFDocument, StandardFonts, rgb, PageSizes } from 'pdf-lib';
import { writeFileSync, readFileSync } from 'fs';

// =============================================================================
// CONSTANTS
// =============================================================================

// Common page sizes (width x height in points, 72 points = 1 inch)
const PAGE_SIZES = {
  LETTER: PageSizes.Letter, // [612, 792] - 8.5" x 11"
  A4: PageSizes.A4, // [595.28, 841.89] - 210mm x 297mm
  LEGAL: [612, 1008] as [number, number], // 8.5" x 14"
};

// Colors
const COLORS = {
  black: rgb(0, 0, 0),
  white: rgb(1, 1, 1),
  gray: rgb(0.5, 0.5, 0.5),
  lightGray: rgb(0.9, 0.9, 0.9),
  primary: rgb(0.2, 0.4, 0.8), // Blue
  success: rgb(0.2, 0.6, 0.2), // Green
  danger: rgb(0.8, 0.2, 0.2), // Red
};

// =============================================================================
// DOCUMENT CREATION
// =============================================================================

async function createDocument(): Promise<PDFDocument> {
  const pdfDoc = await PDFDocument.create();

  // Set document metadata
  pdfDoc.setTitle('Monthly Report');
  pdfDoc.setAuthor('Your Company');
  pdfDoc.setSubject('Sales Report for January 2026');
  pdfDoc.setCreationDate(new Date());

  // Embed fonts
  const helvetica = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  // -------------------------------------------------------------------------
  // PAGE 1: Title Page
  // -------------------------------------------------------------------------
  const page1 = pdfDoc.addPage(PAGE_SIZES.LETTER);
  const { width, height } = page1.getSize();

  // Header bar
  page1.drawRectangle({
    x: 0,
    y: height - 100,
    width: width,
    height: 100,
    color: COLORS.primary,
  });

  // Title
  page1.drawText('Monthly Sales Report', {
    x: 50,
    y: height - 60,
    size: 28,
    font: helveticaBold,
    color: COLORS.white,
  });

  // Subtitle
  page1.drawText('January 2026', {
    x: 50,
    y: height - 85,
    size: 14,
    font: helvetica,
    color: rgb(0.8, 0.9, 1),
  });

  // Main content area
  const contentY = height - 150;

  page1.drawText('Executive Summary', {
    x: 50,
    y: contentY,
    size: 18,
    font: helveticaBold,
    color: COLORS.black,
  });

  // Horizontal line
  page1.drawLine({
    start: { x: 50, y: contentY - 10 },
    end: { x: width - 50, y: contentY - 10 },
    thickness: 1,
    color: COLORS.lightGray,
  });

  // Body text
  const bodyText = [
    'This report summarizes the sales performance for January 2026.',
    'Overall, we achieved 115% of our monthly target.',
    '',
    'Key Highlights:',
    '• Revenue increased by 23% compared to last month',
    '• New customer acquisitions up 18%',
    '• Customer retention rate at 94%',
  ];

  let textY = contentY - 40;
  for (const line of bodyText) {
    page1.drawText(line, {
      x: 50,
      y: textY,
      size: 12,
      font: helvetica,
      color: COLORS.black,
    });
    textY -= 20;
  }

  // Stats boxes
  const statsY = textY - 40;
  const boxWidth = 150;
  const boxHeight = 80;
  const stats = [
    { label: 'Revenue', value: '$1.2M', color: COLORS.success },
    { label: 'Growth', value: '+23%', color: COLORS.primary },
    { label: 'Customers', value: '1,245', color: COLORS.primary },
  ];

  stats.forEach((stat, i) => {
    const boxX = 50 + i * (boxWidth + 20);

    // Box background
    page1.drawRectangle({
      x: boxX,
      y: statsY,
      width: boxWidth,
      height: boxHeight,
      color: COLORS.lightGray,
      borderColor: stat.color,
      borderWidth: 2,
    });

    // Value
    page1.drawText(stat.value, {
      x: boxX + 15,
      y: statsY + 45,
      size: 24,
      font: helveticaBold,
      color: stat.color,
    });

    // Label
    page1.drawText(stat.label, {
      x: boxX + 15,
      y: statsY + 15,
      size: 12,
      font: helvetica,
      color: COLORS.gray,
    });
  });

  // Footer
  page1.drawText('Confidential - Internal Use Only', {
    x: 50,
    y: 30,
    size: 10,
    font: helvetica,
    color: COLORS.gray,
  });

  page1.drawText('Page 1 of 2', {
    x: width - 100,
    y: 30,
    size: 10,
    font: helvetica,
    color: COLORS.gray,
  });

  // -------------------------------------------------------------------------
  // PAGE 2: Data Table
  // -------------------------------------------------------------------------
  const page2 = pdfDoc.addPage(PAGE_SIZES.LETTER);

  page2.drawText('Sales by Region', {
    x: 50,
    y: height - 50,
    size: 18,
    font: helveticaBold,
    color: COLORS.black,
  });

  // Table
  const tableData = [
    ['Region', 'Target', 'Actual', 'Variance'],
    ['North America', '$500,000', '$575,000', '+15%'],
    ['EMEA', '$300,000', '$342,000', '+14%'],
    ['APAC', '$200,000', '$178,000', '-11%'],
    ['LATAM', '$100,000', '$121,000', '+21%'],
  ];

  const tableX = 50;
  let tableY = height - 100;
  const colWidths = [150, 100, 100, 100];
  const rowHeight = 25;

  tableData.forEach((row, rowIndex) => {
    let cellX = tableX;

    // Row background
    if (rowIndex === 0) {
      page2.drawRectangle({
        x: tableX,
        y: tableY - 5,
        width: colWidths.reduce((a, b) => a + b, 0),
        height: rowHeight,
        color: COLORS.primary,
      });
    }

    row.forEach((cell, colIndex) => {
      const textColor =
        rowIndex === 0
          ? COLORS.white
          : colIndex === 3
            ? cell.startsWith('+')
              ? COLORS.success
              : COLORS.danger
            : COLORS.black;

      page2.drawText(cell, {
        x: cellX + 5,
        y: tableY,
        size: 11,
        font: rowIndex === 0 ? helveticaBold : helvetica,
        color: textColor,
      });

      cellX += colWidths[colIndex];
    });

    tableY -= rowHeight;
  });

  // Footer
  page2.drawText('Page 2 of 2', {
    x: width - 100,
    y: 30,
    size: 10,
    font: helvetica,
    color: COLORS.gray,
  });

  return pdfDoc;
}

// =============================================================================
// EXPORT FUNCTIONS
// =============================================================================

/**
 * Save to file (Node.js only)
 */
async function saveToFile(pdfDoc: PDFDocument, filename: string) {
  const pdfBytes = await pdfDoc.save();
  writeFileSync(filename, pdfBytes);
  console.log(`✅ Saved: ${filename}`);
}

/**
 * Get as Uint8Array (all environments)
 */
async function toBytes(pdfDoc: PDFDocument): Promise<Uint8Array> {
  return await pdfDoc.save();
}

/**
 * Get as Response (Cloudflare Workers)
 */
async function toResponse(
  pdfDoc: PDFDocument,
  filename: string
): Promise<Response> {
  const pdfBytes = await pdfDoc.save();
  return new Response(pdfBytes, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  });
}

/**
 * Get as base64 (Browser)
 */
async function toBase64(pdfDoc: PDFDocument): Promise<string> {
  const pdfBytes = await pdfDoc.save();
  // Convert Uint8Array to base64
  let binary = '';
  for (let i = 0; i < pdfBytes.length; i++) {
    binary += String.fromCharCode(pdfBytes[i]);
  }
  return btoa(binary);
}

// =============================================================================
// UTILITY: Add image to PDF
// =============================================================================

async function addImageToPdf(
  pdfDoc: PDFDocument,
  pageIndex: number,
  imageBytes: Uint8Array,
  options: { x: number; y: number; width: number; height: number; type: 'png' | 'jpg' }
) {
  const page = pdfDoc.getPage(pageIndex);
  const image =
    options.type === 'png'
      ? await pdfDoc.embedPng(imageBytes)
      : await pdfDoc.embedJpg(imageBytes);

  page.drawImage(image, {
    x: options.x,
    y: options.y,
    width: options.width,
    height: options.height,
  });
}

// =============================================================================
// MAIN
// =============================================================================

async function main() {
  console.log('Creating PDF document...');

  const pdfDoc = await createDocument();
  await saveToFile(pdfDoc, 'report.pdf');

  console.log('Done! Open report.pdf to view.');
}

// Run if executed directly
main().catch(console.error);

// Export for use as module
export {
  createDocument,
  saveToFile,
  toBytes,
  toResponse,
  toBase64,
  addImageToPdf,
  PAGE_SIZES,
  COLORS,
};
