# pdf-lib - Quick API Reference

**Package**: `pdf-lib` | **Version**: 1.17.1+ | **Docs**: https://pdf-lib.js.org

## Installation

```bash
npm install pdf-lib
```

## Core Imports

```typescript
import {
  PDFDocument,
  StandardFonts,
  rgb,
  PageSizes,
  degrees,
  grayscale,
} from 'pdf-lib';
```

## Create Document

```typescript
const pdfDoc = await PDFDocument.create();
```

## Load Existing PDF

```typescript
// From bytes
const pdfDoc = await PDFDocument.load(existingPdfBytes);

// From base64
const pdfDoc = await PDFDocument.load(base64String);

// Ignore encryption (for copying pages)
const pdfDoc = await PDFDocument.load(bytes, { ignoreEncryption: true });
```

## Document Metadata

```typescript
pdfDoc.setTitle('Document Title');
pdfDoc.setAuthor('Author Name');
pdfDoc.setSubject('Subject');
pdfDoc.setKeywords(['keyword1', 'keyword2']);
pdfDoc.setProducer('Producer App');
pdfDoc.setCreator('Creator App');
pdfDoc.setCreationDate(new Date());
pdfDoc.setModificationDate(new Date());
```

## Pages

```typescript
// Add page with custom size
const page = pdfDoc.addPage([612, 792]);  // Width x Height in points

// Add page with preset size
const page = pdfDoc.addPage(PageSizes.Letter);
const page = pdfDoc.addPage(PageSizes.A4);

// Get page dimensions
const { width, height } = page.getSize();

// Get existing page
const page = pdfDoc.getPage(0);  // 0-indexed

// Get page count
const pageCount = pdfDoc.getPageCount();

// Remove page
pdfDoc.removePage(0);

// Insert page at index
pdfDoc.insertPage(0, page);
```

## Page Sizes (Width x Height in points)

| Size | Dimensions | Inches |
|------|------------|--------|
| `PageSizes.Letter` | [612, 792] | 8.5" × 11" |
| `PageSizes.A4` | [595.28, 841.89] | 210mm × 297mm |
| `PageSizes.Legal` | [612, 1008] | 8.5" × 14" |
| `PageSizes.Tabloid` | [792, 1224] | 11" × 17" |
| `PageSizes.A3` | [841.89, 1190.55] | 297mm × 420mm |
| `PageSizes.A5` | [419.53, 595.28] | 148mm × 210mm |

**Note**: 72 points = 1 inch

## Fonts

```typescript
// Embed standard font
const helvetica = await pdfDoc.embedFont(StandardFonts.Helvetica);
const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
const timesRoman = await pdfDoc.embedFont(StandardFonts.TimesRoman);
const courier = await pdfDoc.embedFont(StandardFonts.Courier);

// Embed custom font
import { readFileSync } from 'fs';
const fontBytes = readFileSync('path/to/font.ttf');
const customFont = await pdfDoc.embedFont(fontBytes);

// Get font metrics
const textWidth = font.widthOfTextAtSize('Hello', 12);
const textHeight = font.heightAtSize(12);
```

## Standard Fonts

```typescript
StandardFonts.Helvetica
StandardFonts.HelveticaBold
StandardFonts.HelveticaOblique
StandardFonts.HelveticaBoldOblique
StandardFonts.TimesRoman
StandardFonts.TimesRomanBold
StandardFonts.TimesRomanItalic
StandardFonts.TimesRomanBoldItalic
StandardFonts.Courier
StandardFonts.CourierBold
StandardFonts.CourierOblique
StandardFonts.CourierBoldOblique
StandardFonts.Symbol
StandardFonts.ZapfDingbats
```

## Colors

```typescript
// RGB (values 0-1)
const red = rgb(1, 0, 0);
const green = rgb(0, 1, 0);
const blue = rgb(0, 0, 1);
const custom = rgb(0.2, 0.4, 0.8);

// Grayscale (0 = black, 1 = white)
const black = grayscale(0);
const gray = grayscale(0.5);
const white = grayscale(1);
```

## Draw Text

```typescript
page.drawText('Hello World', {
  x: 50,
  y: 700,              // From BOTTOM of page!
  size: 12,
  font: helvetica,
  color: rgb(0, 0, 0),
  opacity: 1,
  rotate: degrees(0),  // Rotation angle
  lineHeight: 14,      // For multi-line text
  maxWidth: 500,       // Wrap text at width
});
```

## Draw Shapes

```typescript
// Rectangle
page.drawRectangle({
  x: 50,
  y: 500,
  width: 200,
  height: 100,
  color: rgb(0.9, 0.9, 0.9),      // Fill color
  borderColor: rgb(0, 0, 0),      // Border color
  borderWidth: 1,
  opacity: 1,
  borderOpacity: 1,
});

// Circle
page.drawCircle({
  x: 150,             // Center X
  y: 400,             // Center Y
  size: 50,           // Radius
  color: rgb(1, 0, 0),
  borderColor: rgb(0, 0, 0),
  borderWidth: 1,
});

// Ellipse
page.drawEllipse({
  x: 150,
  y: 300,
  xScale: 100,        // Horizontal radius
  yScale: 50,         // Vertical radius
  color: rgb(0, 1, 0),
});

// Line
page.drawLine({
  start: { x: 50, y: 200 },
  end: { x: 200, y: 200 },
  thickness: 2,
  color: rgb(0, 0, 0),
  opacity: 1,
  dashArray: [5, 3],  // Optional: dashed line
});

// Square (convenience)
page.drawSquare({
  x: 50,
  y: 100,
  size: 50,
  color: rgb(0, 0, 1),
});
```

## Draw Images

```typescript
// Embed PNG
const pngImage = await pdfDoc.embedPng(pngBytes);

// Embed JPG
const jpgImage = await pdfDoc.embedJpg(jpgBytes);

// Draw image
page.drawImage(pngImage, {
  x: 50,
  y: 500,
  width: 200,
  height: 100,
  opacity: 1,
  rotate: degrees(0),
});

// Get image dimensions
const { width, height } = pngImage.size();
const scaled = pngImage.scale(0.5);  // Scale to 50%
```

## Copy Pages from Another PDF

```typescript
const srcPdf = await PDFDocument.load(srcBytes);
const destPdf = await PDFDocument.create();

// Copy specific pages
const [page1, page3] = await destPdf.copyPages(srcPdf, [0, 2]);
destPdf.addPage(page1);
destPdf.addPage(page3);

// Copy all pages
const pages = await destPdf.copyPages(srcPdf, srcPdf.getPageIndices());
pages.forEach(page => destPdf.addPage(page));
```

## Form Fields (AcroForms)

```typescript
// Get form
const form = pdfDoc.getForm();

// Get text field
const nameField = form.getTextField('name');
nameField.setText('John Doe');

// Get checkbox
const checkbox = form.getCheckBox('agree');
checkbox.check();
// checkbox.uncheck();

// Get dropdown
const dropdown = form.getDropdown('country');
dropdown.select('USA');

// Get radio group
const radio = form.getRadioGroup('gender');
radio.select('male');

// Flatten form (make fields uneditable)
form.flatten();
```

## Export

```typescript
// Get as Uint8Array
const pdfBytes = await pdfDoc.save();

// Node.js - save to file
import { writeFileSync } from 'fs';
writeFileSync('output.pdf', pdfBytes);

// Cloudflare Workers - HTTP response
const pdfBytes = await pdfDoc.save();
return new Response(pdfBytes, {
  headers: {
    'Content-Type': 'application/pdf',
    'Content-Disposition': 'attachment; filename="document.pdf"',
  },
});

// Browser - download
const blob = new Blob([pdfBytes], { type: 'application/pdf' });
const url = URL.createObjectURL(blob);

// Get as base64
const base64 = await pdfDoc.saveAsBase64();
const dataUri = await pdfDoc.saveAsBase64({ dataUri: true });
```

## Coordinate System

**CRITICAL**: PDF coordinate origin is at **BOTTOM-LEFT**, not top-left!

```
(0, height) -------- (width, height)
     |                    |
     |     PDF Page       |
     |                    |
   (0, 0) ---------- (width, 0)
```

To position from top:
```typescript
const { height } = page.getSize();
const yFromTop = height - 50;  // 50 points from top
page.drawText('Near top', { x: 50, y: yFromTop, ... });
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Y coordinate from top | Calculate from bottom: `height - y` |
| RGB values 0-255 | RGB values are 0-1 (divide by 255) |
| Forgot await on embed | Always `await pdfDoc.embedFont()` |
| Forgot await on save | Always `await pdfDoc.save()` |
| Wrong image format | Use `embedPng` for PNG, `embedJpg` for JPG |

## Units Reference

| Unit | Points |
|------|--------|
| 1 inch | 72 |
| 1 cm | 28.35 |
| 1 mm | 2.835 |

## Measure Text for Layout

```typescript
const text = 'Hello World';
const fontSize = 12;
const textWidth = font.widthOfTextAtSize(text, fontSize);
const textHeight = font.heightAtSize(fontSize);

// Center text horizontally
const x = (pageWidth - textWidth) / 2;

// Right-align text
const x = pageWidth - textWidth - margin;
```
