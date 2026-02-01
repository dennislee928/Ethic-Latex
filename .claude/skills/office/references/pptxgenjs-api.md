# pptxgenjs - Quick API Reference

**Package**: `pptxgenjs` | **Version**: 4.0.1+ | **Docs**: https://gitbrent.github.io/PptxGenJS/

## Installation

```bash
npm install pptxgenjs
```

## Core Import

```typescript
import pptxgen from 'pptxgenjs';
```

## Create Presentation

```typescript
const pptx = new pptxgen();

// Metadata
pptx.author = 'Author Name';
pptx.title = 'Presentation Title';
pptx.subject = 'Subject';
pptx.company = 'Company Name';

// Layout (default is LAYOUT_16x9)
pptx.layout = 'LAYOUT_16x9';  // or 'LAYOUT_4x3', 'LAYOUT_WIDE'
```

## Add Slide

```typescript
const slide = pptx.addSlide();

// With master layout
const slide = pptx.addSlide({ masterName: 'MASTER_SLIDE' });
```

## Text

```typescript
// Simple text
slide.addText('Hello World', {
  x: 1, y: 1, w: 8, h: 1,
  fontSize: 24,
  color: '333333',
  bold: true,
  italic: false,
  align: 'center',  // 'left', 'center', 'right'
  valign: 'middle', // 'top', 'middle', 'bottom'
});

// Multiple text runs with different formatting
slide.addText([
  { text: 'Bold text', options: { bold: true, fontSize: 18 } },
  { text: ' and ', options: { fontSize: 18 } },
  { text: 'colored text', options: { color: 'FF0000', fontSize: 18 } },
], { x: 1, y: 2, w: 8, h: 0.5 });

// Bullet points
slide.addText([
  { text: 'First point', options: { bullet: true } },
  { text: 'Second point', options: { bullet: true } },
  { text: 'Third point', options: { bullet: true } },
], { x: 1, y: 1, w: 8, h: 3 });
```

## Text Options

| Option | Type | Description |
|--------|------|-------------|
| `x`, `y` | number | Position in inches |
| `w`, `h` | number | Width/height in inches |
| `fontSize` | number | Font size in points |
| `fontFace` | string | Font family name |
| `color` | string | Hex color (without #) |
| `bold` | boolean | Bold text |
| `italic` | boolean | Italic text |
| `underline` | object | `{ style: 'sng' }` |
| `align` | string | 'left', 'center', 'right' |
| `valign` | string | 'top', 'middle', 'bottom' |
| `bullet` | boolean | Show bullet point |
| `fill` | object | `{ color: 'F0F0F0' }` |
| `rotate` | number | Rotation in degrees |

## Tables

```typescript
const tableData = [
  // Header row
  [
    { text: 'Name', options: { bold: true, fill: '0066CC', color: 'FFFFFF' } },
    { text: 'Value', options: { bold: true, fill: '0066CC', color: 'FFFFFF' } },
  ],
  // Data rows
  ['Item 1', '$100'],
  ['Item 2', '$200'],
  [{ text: 'Total', options: { bold: true } }, { text: '$300', options: { bold: true } }],
];

slide.addTable(tableData, {
  x: 0.5, y: 1, w: 9,
  colW: [5, 4],           // Column widths
  border: { pt: 1, color: 'CCCCCC' },
  fontFace: 'Arial',
  fontSize: 14,
  align: 'center',
  valign: 'middle',
  rowH: 0.5,              // Row height
});
```

## Charts

### Line Chart

```typescript
slide.addChart(pptx.ChartType.line, [
  { name: 'Series 1', labels: ['Jan', 'Feb', 'Mar'], values: [100, 150, 200] },
  { name: 'Series 2', labels: ['Jan', 'Feb', 'Mar'], values: [80, 120, 180] },
], {
  x: 0.5, y: 1, w: 9, h: 4,
  showLegend: true,
  legendPos: 'b',         // 'b', 't', 'l', 'r'
  showTitle: false,
  lineDataSymbol: 'circle',
  chartColors: ['0066CC', 'FF6600'],
});
```

### Bar Chart

```typescript
slide.addChart(pptx.ChartType.bar, [
  { name: '2025', labels: ['Q1', 'Q2', 'Q3', 'Q4'], values: [100, 120, 110, 130] },
  { name: '2026', labels: ['Q1', 'Q2', 'Q3', 'Q4'], values: [120, 140, 130, 150] },
], {
  x: 0.5, y: 1, w: 9, h: 4,
  barDir: 'bar',          // 'bar' (horizontal) or 'col' (vertical)
  showValue: true,
  chartColors: ['0066CC', 'CCCCCC'],
});
```

### Pie Chart

```typescript
slide.addChart(pptx.ChartType.pie, [
  { name: 'Sales', labels: ['Product A', 'Product B', 'Product C'], values: [45, 30, 25] },
], {
  x: 0.5, y: 1, w: 5, h: 4,
  showLegend: true,
  showPercent: true,
  chartColors: ['0066CC', '00AA44', 'FF6600'],
});
```

### Chart Types

```typescript
pptx.ChartType.line
pptx.ChartType.bar
pptx.ChartType.area
pptx.ChartType.pie
pptx.ChartType.doughnut
pptx.ChartType.scatter
```

## Images

```typescript
// From file path (Node.js)
slide.addImage({
  path: 'logo.png',
  x: 0.5, y: 0.5, w: 2, h: 1,
});

// From base64
slide.addImage({
  data: 'image/png;base64,iVBORw0KGgo...',
  x: 0.5, y: 2, w: 4, h: 3,
});

// From URL (Node.js only - uses https module)
slide.addImage({
  path: 'https://example.com/image.png',
  x: 5, y: 2, w: 4, h: 3,
});

// Hyperlink on image
slide.addImage({
  path: 'logo.png',
  x: 0.5, y: 0.5, w: 2, h: 1,
  hyperlink: { url: 'https://example.com' },
});
```

## Shapes

```typescript
// Rectangle
slide.addShape(pptx.ShapeType.rect, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: '0066CC' },
  line: { color: '004499', pt: 2 },
});

// Circle/Ellipse
slide.addShape(pptx.ShapeType.ellipse, {
  x: 5, y: 1, w: 2, h: 2,
  fill: { color: '00AA00' },
});

// Line
slide.addShape(pptx.ShapeType.line, {
  x: 0.5, y: 3, w: 9, h: 0,
  line: { color: '333333', pt: 1 },
});

// Arrow
slide.addShape(pptx.ShapeType.rightArrow, {
  x: 1, y: 4, w: 2, h: 0.5,
  fill: { color: 'FF6600' },
});
```

### Shape Types

```typescript
pptx.ShapeType.rect
pptx.ShapeType.ellipse
pptx.ShapeType.roundRect
pptx.ShapeType.triangle
pptx.ShapeType.line
pptx.ShapeType.rightArrow
pptx.ShapeType.leftArrow
pptx.ShapeType.upArrow
pptx.ShapeType.downArrow
pptx.ShapeType.star5
pptx.ShapeType.heart
```

## Slide Masters

```typescript
// Define master slide
pptx.defineSlideMaster({
  title: 'COMPANY_MASTER',
  background: { color: 'FFFFFF' },
  objects: [
    { text: { text: 'Company Name', options: { x: 0.5, y: 0.2, fontSize: 10, color: '999999' } } },
    { line: { x: 0.5, y: 0.5, w: 9, h: 0, line: { color: '0066CC', pt: 2 } } },
    { image: { path: 'logo.png', x: 8.5, y: 0.1, w: 1, h: 0.4 } },
  ],
});

// Use master
const slide = pptx.addSlide({ masterName: 'COMPANY_MASTER' });
```

## Export

```typescript
// Node.js - Save to file
await pptx.writeFile({ fileName: 'presentation.pptx' });

// Browser - Trigger download (same API)
await pptx.writeFile({ fileName: 'presentation.pptx' });

// Get as base64
const base64 = await pptx.write({ outputType: 'base64' });

// Get as ArrayBuffer
const buffer = await pptx.write({ outputType: 'arraybuffer' });

// Get as Blob (browser)
const blob = await pptx.write({ outputType: 'blob' });

// Cloudflare Workers - Response
const buffer = await pptx.write({ outputType: 'arraybuffer' });
return new Response(buffer, {
  headers: {
    'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'Content-Disposition': 'attachment; filename="presentation.pptx"',
  },
});
```

## Output Types

| Type | Return | Use Case |
|------|--------|----------|
| `base64` | string | Email attachments, APIs |
| `arraybuffer` | ArrayBuffer | Workers, general |
| `blob` | Blob | Browser downloads |
| `uint8array` | Uint8Array | Binary manipulation |
| `nodebuffer` | Buffer | Node.js file operations |

## Units

Default units are **inches**. Can change globally:

```typescript
pptx.defineLayout({
  name: 'LAYOUT_CUSTOM',
  width: 10,    // inches
  height: 7.5,  // inches
});
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting await on write/writeFile | Always `await pptx.writeFile()` |
| Color with # (`'#0066CC'`) | Omit # (`'0066CC'`) |
| Using path URL in Workers | Use base64 data instead |
| Positions in pixels | Positions are in inches |

## Workers Compatibility

pptxgenjs works in Workers **except** for remote image URLs (uses `https` module).

**Workaround**: Fetch images first, convert to base64:

```typescript
// In Workers, fetch image first
const imageResponse = await fetch('https://example.com/image.png');
const imageBuffer = await imageResponse.arrayBuffer();
const base64 = btoa(String.fromCharCode(...new Uint8Array(imageBuffer)));

slide.addImage({
  data: `image/png;base64,${base64}`,
  x: 1, y: 1, w: 4, h: 3,
});
```
