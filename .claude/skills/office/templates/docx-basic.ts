/**
 * DOCX Basic Template - Word Document Generation
 *
 * Creates a professional document with:
 * - Title and headings
 * - Formatted paragraphs
 * - Tables with styling
 * - Images
 *
 * Works in: Node.js, Cloudflare Workers, Browser
 *
 * Usage:
 *   npm install docx
 *   npx tsx docx-basic.ts
 */

import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  WidthType,
  HeadingLevel,
  AlignmentType,
  BorderStyle,
  ImageRun,
} from 'docx';
import { writeFileSync, readFileSync } from 'fs';

// =============================================================================
// DOCUMENT CREATION
// =============================================================================

async function createDocument() {
  const doc = new Document({
    // Document metadata
    creator: 'Your Company',
    title: 'Sample Report',
    description: 'A sample document created with docx',

    sections: [
      {
        children: [
          // ---------------------------------------------------------------------
          // TITLE
          // ---------------------------------------------------------------------
          new Paragraph({
            text: 'Monthly Sales Report',
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
          }),

          new Paragraph({
            children: [
              new TextRun({
                text: 'January 2026',
                italics: true,
                color: '666666',
              }),
            ],
            alignment: AlignmentType.CENTER,
          }),

          // Spacer
          new Paragraph({ text: '' }),

          // ---------------------------------------------------------------------
          // HEADING 1
          // ---------------------------------------------------------------------
          new Paragraph({
            text: 'Executive Summary',
            heading: HeadingLevel.HEADING_1,
          }),

          // ---------------------------------------------------------------------
          // FORMATTED PARAGRAPHS
          // ---------------------------------------------------------------------
          new Paragraph({
            children: [
              new TextRun('This report summarizes the sales performance for '),
              new TextRun({ text: 'January 2026', bold: true }),
              new TextRun('. Overall, we achieved '),
              new TextRun({ text: '115%', bold: true, color: '00AA00' }),
              new TextRun(' of our monthly target.'),
            ],
          }),

          new Paragraph({
            children: [
              new TextRun({
                text: 'Key highlights include:',
                italics: true,
              }),
            ],
          }),

          // Bullet points (using simple paragraphs with bullet character)
          new Paragraph({
            text: '• Revenue increased by 23% compared to last month',
            indent: { left: 720 }, // 720 twips = 0.5 inch
          }),
          new Paragraph({
            text: '• New customer acquisitions up 18%',
            indent: { left: 720 },
          }),
          new Paragraph({
            text: '• Customer retention rate at 94%',
            indent: { left: 720 },
          }),

          // Spacer
          new Paragraph({ text: '' }),

          // ---------------------------------------------------------------------
          // HEADING 2
          // ---------------------------------------------------------------------
          new Paragraph({
            text: 'Sales by Region',
            heading: HeadingLevel.HEADING_2,
          }),

          // ---------------------------------------------------------------------
          // TABLE
          // ---------------------------------------------------------------------
          createSalesTable(),

          // Spacer
          new Paragraph({ text: '' }),

          // ---------------------------------------------------------------------
          // HEADING 2
          // ---------------------------------------------------------------------
          new Paragraph({
            text: 'Conclusion',
            heading: HeadingLevel.HEADING_2,
          }),

          new Paragraph({
            children: [
              new TextRun(
                'The strong performance this month positions us well for Q1 targets. '
              ),
              new TextRun({
                text: 'Recommended actions',
                bold: true,
              }),
              new TextRun(
                ' include increasing marketing spend in the APAC region and expanding the sales team in EMEA.'
              ),
            ],
          }),

          // ---------------------------------------------------------------------
          // FOOTER NOTE
          // ---------------------------------------------------------------------
          new Paragraph({ text: '' }),
          new Paragraph({
            children: [
              new TextRun({
                text: 'Report generated automatically on ' +
                  new Date().toISOString().split('T')[0],
                size: 20, // 10pt (size is in half-points)
                color: '999999',
              }),
            ],
            alignment: AlignmentType.RIGHT,
          }),
        ],
      },
    ],
  });

  return doc;
}

// =============================================================================
// TABLE HELPER
// =============================================================================

function createSalesTable(): Table {
  const data = [
    ['Region', 'Target', 'Actual', 'Variance'],
    ['North America', '$500,000', '$575,000', '+15%'],
    ['EMEA', '$300,000', '$342,000', '+14%'],
    ['APAC', '$200,000', '$178,000', '-11%'],
    ['LATAM', '$100,000', '$121,000', '+21%'],
    ['Total', '$1,100,000', '$1,216,000', '+10.5%'],
  ];

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: data.map((row, rowIndex) =>
      new TableRow({
        children: row.map(
          (cell, cellIndex) =>
            new TableCell({
              children: [
                new Paragraph({
                  children: [
                    new TextRun({
                      text: cell,
                      bold: rowIndex === 0 || rowIndex === data.length - 1,
                      color:
                        cellIndex === 3 && rowIndex > 0
                          ? cell.startsWith('+')
                            ? '00AA00'
                            : 'CC0000'
                          : '000000',
                    }),
                  ],
                  alignment:
                    cellIndex === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT,
                }),
              ],
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
                left: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
                right: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
              },
              shading:
                rowIndex === 0
                  ? { fill: 'F0F0F0' }
                  : rowIndex === data.length - 1
                    ? { fill: 'E8F4E8' }
                    : undefined,
            })
        ),
      })
    ),
  });
}

// =============================================================================
// IMAGE HELPER (uncomment if you have an image)
// =============================================================================

// function createImageParagraph(imagePath: string): Paragraph {
//   const imageBuffer = readFileSync(imagePath);
//   return new Paragraph({
//     children: [
//       new ImageRun({
//         data: imageBuffer,
//         transformation: { width: 200, height: 100 },
//         type: 'png', // or 'jpg'
//       }),
//     ],
//   });
// }

// =============================================================================
// EXPORT FUNCTIONS
// =============================================================================

/**
 * Save to file (Node.js only)
 */
async function saveToFile(doc: Document, filename: string) {
  const buffer = await Packer.toBuffer(doc);
  writeFileSync(filename, buffer);
  console.log(`✅ Saved: ${filename}`);
}

/**
 * Get as Response (Cloudflare Workers)
 */
async function toResponse(doc: Document, filename: string): Promise<Response> {
  const buffer = await Packer.toBuffer(doc);
  return new Response(buffer, {
    headers: {
      'Content-Type':
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  });
}

/**
 * Get as Blob (Browser)
 */
async function toBlob(doc: Document): Promise<Blob> {
  return await Packer.toBlob(doc);
}

// =============================================================================
// MAIN
// =============================================================================

async function main() {
  console.log('Creating Word document...');

  const doc = await createDocument();
  await saveToFile(doc, 'report.docx');

  console.log('Done! Open report.docx to view.');
}

// Run if executed directly
main().catch(console.error);

// Export for use as module
export { createDocument, saveToFile, toResponse, toBlob };
