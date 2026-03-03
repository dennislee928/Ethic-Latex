/**
 * PPTX Basic Template - PowerPoint Generation with pptxgenjs
 *
 * This template demonstrates:
 * - Creating presentations with multiple slides
 * - Title slides, content slides, chart slides
 * - Tables, bullet points, shapes
 * - Export to file, buffer, base64
 *
 * Usage:
 *   npm install pptxgenjs
 *   npx tsx pptx-basic.ts
 */

import pptxgen from 'pptxgenjs';
import { writeFileSync } from 'fs';

// ============================================================================
// Create Presentation
// ============================================================================

const pptx = new pptxgen();

// Set presentation metadata
pptx.author = 'Office Skill';
pptx.title = 'Quarterly Business Review';
pptx.subject = 'Q1 2026 Performance';
pptx.company = 'Acme Corporation';

// ============================================================================
// Slide 1: Title Slide
// ============================================================================

const titleSlide = pptx.addSlide();

titleSlide.addText('Quarterly Business Review', {
  x: 0.5,
  y: 2,
  w: 9,
  h: 1.2,
  fontSize: 44,
  bold: true,
  color: '0066CC',
  align: 'center',
});

titleSlide.addText('Q1 2026', {
  x: 0.5,
  y: 3.5,
  w: 9,
  h: 0.6,
  fontSize: 28,
  color: '666666',
  align: 'center',
});

titleSlide.addText('Presented by: Business Intelligence Team', {
  x: 0.5,
  y: 4.5,
  w: 9,
  h: 0.4,
  fontSize: 14,
  color: '999999',
  align: 'center',
});

// ============================================================================
// Slide 2: Key Highlights (Bullet Points)
// ============================================================================

const highlightsSlide = pptx.addSlide();

highlightsSlide.addText('Key Highlights', {
  x: 0.5,
  y: 0.3,
  w: 9,
  h: 0.8,
  fontSize: 32,
  bold: true,
  color: '333333',
});

// Separator line
highlightsSlide.addShape(pptx.ShapeType.line, {
  x: 0.5,
  y: 1.0,
  w: 9,
  h: 0,
  line: { color: '0066CC', width: 2 },
});

highlightsSlide.addText(
  [
    {
      text: 'Revenue increased 25% year-over-year to $12.5M',
      options: { bullet: true, fontSize: 20 },
    },
    {
      text: 'Customer base grew from 8,000 to 10,500 accounts',
      options: { bullet: true, fontSize: 20 },
    },
    {
      text: 'Successfully launched 3 new product features',
      options: { bullet: true, fontSize: 20 },
    },
    {
      text: 'Expanded operations to 5 new markets',
      options: { bullet: true, fontSize: 20 },
    },
    {
      text: 'Net Promoter Score improved from 45 to 62',
      options: { bullet: true, fontSize: 20 },
    },
  ],
  {
    x: 0.5,
    y: 1.3,
    w: 8.5,
    h: 4,
    valign: 'top',
    color: '333333',
  }
);

// ============================================================================
// Slide 3: Financial Summary (Table)
// ============================================================================

const tableSlide = pptx.addSlide();

tableSlide.addText('Financial Summary', {
  x: 0.5,
  y: 0.3,
  w: 9,
  h: 0.8,
  fontSize: 32,
  bold: true,
  color: '333333',
});

const tableData = [
  [
    { text: 'Metric', options: { bold: true, fill: '0066CC', color: 'FFFFFF' } },
    { text: 'Q1 2025', options: { bold: true, fill: '0066CC', color: 'FFFFFF' } },
    { text: 'Q1 2026', options: { bold: true, fill: '0066CC', color: 'FFFFFF' } },
    { text: 'Change', options: { bold: true, fill: '0066CC', color: 'FFFFFF' } },
  ],
  ['Revenue', '$10.0M', '$12.5M', '+25%'],
  ['Gross Profit', '$6.5M', '$8.4M', '+29%'],
  ['Operating Expenses', '$4.2M', '$4.8M', '+14%'],
  ['Net Income', '$2.3M', '$3.6M', '+57%'],
  ['Customers', '8,000', '10,500', '+31%'],
];

tableSlide.addTable(tableData, {
  x: 0.5,
  y: 1.3,
  w: 9,
  colW: [2.5, 2, 2, 2.5],
  border: { pt: 1, color: 'CCCCCC' },
  fontFace: 'Arial',
  fontSize: 14,
  align: 'center',
  valign: 'middle',
});

// ============================================================================
// Slide 4: Revenue Trend (Chart)
// ============================================================================

const chartSlide = pptx.addSlide();

chartSlide.addText('Revenue Trend', {
  x: 0.5,
  y: 0.3,
  w: 9,
  h: 0.6,
  fontSize: 32,
  bold: true,
  color: '333333',
});

chartSlide.addChart(pptx.ChartType.line, [
  {
    name: 'Revenue ($M)',
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    values: [1.8, 2.1, 2.4, 2.2, 2.6, 2.9],
  },
  {
    name: 'Target ($M)',
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    values: [2.0, 2.0, 2.2, 2.2, 2.4, 2.4],
  },
], {
  x: 0.5,
  y: 1.0,
  w: 9,
  h: 4.2,
  showLegend: true,
  legendPos: 'b',
  showTitle: false,
  lineDataSymbol: 'circle',
  lineDataSymbolSize: 8,
  chartColors: ['0066CC', '999999'],
});

// ============================================================================
// Slide 5: Regional Performance (Bar Chart)
// ============================================================================

const barSlide = pptx.addSlide();

barSlide.addText('Regional Performance', {
  x: 0.5,
  y: 0.3,
  w: 9,
  h: 0.6,
  fontSize: 32,
  bold: true,
  color: '333333',
});

barSlide.addChart(pptx.ChartType.bar, [
  {
    name: 'Q1 2026',
    labels: ['North America', 'Europe', 'Asia Pacific', 'Latin America'],
    values: [5.2, 3.8, 2.5, 1.0],
  },
  {
    name: 'Q1 2025',
    labels: ['North America', 'Europe', 'Asia Pacific', 'Latin America'],
    values: [4.2, 3.1, 1.9, 0.8],
  },
], {
  x: 0.5,
  y: 1.0,
  w: 9,
  h: 4.2,
  showLegend: true,
  legendPos: 'b',
  showTitle: false,
  barDir: 'bar',
  chartColors: ['0066CC', 'CCCCCC'],
  showValue: true,
  dataLabelPosition: 'outEnd',
});

// ============================================================================
// Slide 6: Next Steps
// ============================================================================

const nextStepsSlide = pptx.addSlide();

nextStepsSlide.addText('Next Steps', {
  x: 0.5,
  y: 0.3,
  w: 9,
  h: 0.8,
  fontSize: 32,
  bold: true,
  color: '333333',
});

// Colored boxes for each action item
const steps = [
  { num: '1', text: 'Complete Q2 product roadmap review', color: '0066CC' },
  { num: '2', text: 'Finalize expansion strategy for APAC region', color: '00AA44' },
  { num: '3', text: 'Launch customer retention program', color: 'FF6600' },
];

steps.forEach((step, index) => {
  const y = 1.3 + index * 1.4;

  // Number circle
  nextStepsSlide.addShape(pptx.ShapeType.ellipse, {
    x: 0.5,
    y: y,
    w: 0.6,
    h: 0.6,
    fill: { color: step.color },
  });

  nextStepsSlide.addText(step.num, {
    x: 0.5,
    y: y,
    w: 0.6,
    h: 0.6,
    fontSize: 20,
    bold: true,
    color: 'FFFFFF',
    align: 'center',
    valign: 'middle',
  });

  // Step text
  nextStepsSlide.addText(step.text, {
    x: 1.3,
    y: y + 0.1,
    w: 7.5,
    h: 0.5,
    fontSize: 18,
    color: '333333',
  });
});

// ============================================================================
// Export Functions
// ============================================================================

// Node.js - Save to file
export async function saveToFile(filename: string = 'presentation.pptx'): Promise<void> {
  await pptx.writeFile({ fileName: filename });
  console.log(`Saved: ${filename}`);
}

// Get as ArrayBuffer (for Workers/Browser)
export async function toArrayBuffer(): Promise<ArrayBuffer> {
  return await pptx.write({ outputType: 'arraybuffer' }) as ArrayBuffer;
}

// Get as base64 (for email/API)
export async function toBase64(): Promise<string> {
  return await pptx.write({ outputType: 'base64' }) as string;
}

// Get as Blob (for browser downloads)
export async function toBlob(): Promise<Blob> {
  return await pptx.write({ outputType: 'blob' }) as Blob;
}

// Cloudflare Workers Response
export async function toResponse(filename: string = 'presentation.pptx'): Promise<Response> {
  const arrayBuffer = await toArrayBuffer();
  return new Response(arrayBuffer, {
    headers: {
      'Content-Type':
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  });
}

// ============================================================================
// Run if executed directly
// ============================================================================

// Check if running directly (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  saveToFile('quarterly-report.pptx').then(() => {
    console.log('✅ PowerPoint presentation created successfully!');
    console.log('   Slides: 6 (Title, Highlights, Table, Line Chart, Bar Chart, Next Steps)');
  });
}
