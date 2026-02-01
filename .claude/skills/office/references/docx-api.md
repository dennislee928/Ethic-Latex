# docx npm - Quick API Reference

**Package**: `docx` | **Version**: 9.5.0+ | **Docs**: https://docx.js.org

## Installation

```bash
npm install docx
```

## Core Imports

```typescript
import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  HeadingLevel,
  AlignmentType,
  WidthType,
  BorderStyle,
  ImageRun,
} from 'docx';
```

## Document Structure

```typescript
const doc = new Document({
  creator: 'Author Name',
  title: 'Document Title',
  description: 'Description',
  sections: [{
    children: [
      // Paragraphs, Tables, etc.
    ],
  }],
});
```

## Paragraph

```typescript
// Simple text
new Paragraph({ text: 'Hello World' })

// With heading
new Paragraph({
  text: 'Title',
  heading: HeadingLevel.HEADING_1,
  alignment: AlignmentType.CENTER,
})

// With formatted runs
new Paragraph({
  children: [
    new TextRun('Normal text'),
    new TextRun({ text: 'Bold', bold: true }),
    new TextRun({ text: 'Italic', italics: true }),
    new TextRun({ text: 'Colored', color: 'FF0000' }),
    new TextRun({ text: 'Sized', size: 24 }), // Half-points (24 = 12pt)
  ],
})

// With indent
new Paragraph({
  text: '• Bullet point',
  indent: { left: 720 }, // Twips (720 = 0.5 inch)
})
```

## TextRun Options

| Option | Type | Description |
|--------|------|-------------|
| `text` | string | The text content |
| `bold` | boolean | Bold text |
| `italics` | boolean | Italic text |
| `underline` | object | `{ type: UnderlineType.SINGLE }` |
| `color` | string | Hex color without # (e.g., 'FF0000') |
| `size` | number | Font size in half-points (24 = 12pt) |
| `font` | string | Font family name |
| `highlight` | string | Highlight color |
| `strike` | boolean | Strikethrough |

## HeadingLevel

```typescript
HeadingLevel.TITLE
HeadingLevel.HEADING_1
HeadingLevel.HEADING_2
HeadingLevel.HEADING_3
HeadingLevel.HEADING_4
HeadingLevel.HEADING_5
HeadingLevel.HEADING_6
```

## AlignmentType

```typescript
AlignmentType.LEFT
AlignmentType.CENTER
AlignmentType.RIGHT
AlignmentType.JUSTIFIED
```

## Table

```typescript
new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: [
    new TableRow({
      children: [
        new TableCell({
          children: [new Paragraph({ text: 'Cell 1' })],
          width: { size: 50, type: WidthType.PERCENTAGE },
          borders: {
            top: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
            bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
            left: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
            right: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
          },
          shading: { fill: 'F0F0F0' },
        }),
        new TableCell({
          children: [new Paragraph({ text: 'Cell 2' })],
        }),
      ],
    }),
  ],
})
```

## WidthType

```typescript
WidthType.PERCENTAGE  // Percentage of page width
WidthType.DXA         // Twips (1/20 of a point)
WidthType.AUTO        // Auto width
```

## BorderStyle

```typescript
BorderStyle.SINGLE
BorderStyle.DOUBLE
BorderStyle.DASHED
BorderStyle.DOTTED
BorderStyle.NONE
```

## Images

```typescript
import { readFileSync } from 'fs';

new Paragraph({
  children: [
    new ImageRun({
      data: readFileSync('image.png'),
      transformation: { width: 200, height: 100 },
      type: 'png', // or 'jpg'
    }),
  ],
})
```

## Export (CRITICAL: Async!)

```typescript
// Node.js - save to file
import { writeFileSync } from 'fs';
const buffer = await Packer.toBuffer(doc);  // MUST await!
writeFileSync('output.docx', buffer);

// Cloudflare Workers - HTTP response
const buffer = await Packer.toBuffer(doc);
return new Response(buffer, {
  headers: {
    'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'Content-Disposition': 'attachment; filename="document.docx"',
  },
});

// Browser - Blob for download
const blob = await Packer.toBlob(doc);
const url = URL.createObjectURL(blob);
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `Packer.toBuffer(doc)` without await | Always `await Packer.toBuffer(doc)` |
| Color with # (`'#FF0000'`) | Omit # (`'FF0000'`) |
| Size in points | Size is half-points (multiply by 2) |
| Indent in inches | Indent is twips (multiply by 1440) |

## Units Reference

| Unit | Conversion |
|------|------------|
| Points to half-points | × 2 |
| Inches to twips | × 1440 |
| cm to twips | × 567 |
