/**
 * Cloudflare Workers PDF Generation
 *
 * Two approaches:
 * 1. pdf-lib: Programmatic PDF creation (included below)
 * 2. Browser Rendering: HTML→PDF with full CSS (requires paid plan)
 *
 * Usage:
 *   wrangler dev
 *   curl http://localhost:8787/invoice/123 > invoice.pdf
 */

import { Hono } from 'hono';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';

// =============================================================================
// TYPES
// =============================================================================

interface Env {
  // For Browser Rendering (optional, paid feature)
  BROWSER?: Fetcher;
}

interface InvoiceData {
  invoiceNumber: string;
  date: string;
  customerName: string;
  customerEmail: string;
  items: Array<{
    description: string;
    quantity: number;
    unitPrice: number;
  }>;
}

// =============================================================================
// APP SETUP
// =============================================================================

const app = new Hono<{ Bindings: Env }>();

// =============================================================================
// ROUTE 1: Generate Invoice PDF with pdf-lib
// =============================================================================

app.get('/invoice/:id', async (c) => {
  const invoiceId = c.req.param('id');

  // In production, fetch this from your database
  const invoiceData: InvoiceData = {
    invoiceNumber: `INV-${invoiceId}`,
    date: new Date().toISOString().split('T')[0],
    customerName: 'Acme Corporation',
    customerEmail: 'billing@acme.com',
    items: [
      { description: 'Web Development Services', quantity: 40, unitPrice: 150 },
      { description: 'UI/UX Design', quantity: 20, unitPrice: 125 },
      { description: 'Hosting (Annual)', quantity: 1, unitPrice: 500 },
    ],
  };

  const pdfBytes = await generateInvoicePdf(invoiceData);

  return new Response(pdfBytes, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="${invoiceData.invoiceNumber}.pdf"`,
    },
  });
});

// =============================================================================
// ROUTE 2: HTML to PDF with Browser Rendering (requires binding)
// =============================================================================

app.get('/report/:id', async (c) => {
  const reportId = c.req.param('id');

  // Check if Browser Rendering is available
  if (!c.env.BROWSER) {
    return c.json(
      {
        error: 'Browser Rendering not configured',
        hint: 'Add browser binding to wrangler.jsonc',
      },
      501
    );
  }

  // For Browser Rendering, you'd use Puppeteer:
  // const puppeteer = await import('@cloudflare/puppeteer');
  // const browser = await puppeteer.launch(c.env.BROWSER);
  // const page = await browser.newPage();
  // await page.setContent(htmlContent);
  // const pdf = await page.pdf({ format: 'A4' });
  // await browser.close();

  // Placeholder response
  return c.json({
    message: 'Browser Rendering endpoint',
    reportId,
    note: 'Implement with @cloudflare/puppeteer for HTML→PDF',
  });
});

// =============================================================================
// PDF GENERATION FUNCTION
// =============================================================================

async function generateInvoicePdf(data: InvoiceData): Promise<Uint8Array> {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([612, 792]); // Letter size
  const { width, height } = page.getSize();

  // Fonts
  const helvetica = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  // Colors
  const black = rgb(0, 0, 0);
  const gray = rgb(0.5, 0.5, 0.5);
  const primary = rgb(0.2, 0.4, 0.8);

  // -------------------------------------------------------------------------
  // HEADER
  // -------------------------------------------------------------------------

  // Company name
  page.drawText('Your Company Name', {
    x: 50,
    y: height - 50,
    size: 20,
    font: helveticaBold,
    color: primary,
  });

  // Invoice label
  page.drawText('INVOICE', {
    x: width - 150,
    y: height - 50,
    size: 24,
    font: helveticaBold,
    color: black,
  });

  // Invoice details
  page.drawText(`Invoice #: ${data.invoiceNumber}`, {
    x: width - 150,
    y: height - 75,
    size: 10,
    font: helvetica,
    color: gray,
  });

  page.drawText(`Date: ${data.date}`, {
    x: width - 150,
    y: height - 90,
    size: 10,
    font: helvetica,
    color: gray,
  });

  // -------------------------------------------------------------------------
  // CUSTOMER INFO
  // -------------------------------------------------------------------------

  page.drawText('Bill To:', {
    x: 50,
    y: height - 120,
    size: 10,
    font: helveticaBold,
    color: gray,
  });

  page.drawText(data.customerName, {
    x: 50,
    y: height - 135,
    size: 12,
    font: helvetica,
    color: black,
  });

  page.drawText(data.customerEmail, {
    x: 50,
    y: height - 150,
    size: 10,
    font: helvetica,
    color: gray,
  });

  // -------------------------------------------------------------------------
  // TABLE HEADER
  // -------------------------------------------------------------------------

  const tableTop = height - 200;
  const colWidths = [250, 80, 100, 100];
  const cols = ['Description', 'Qty', 'Unit Price', 'Amount'];

  // Header background
  page.drawRectangle({
    x: 50,
    y: tableTop - 5,
    width: width - 100,
    height: 25,
    color: rgb(0.95, 0.95, 0.95),
  });

  // Header text
  let colX = 50;
  cols.forEach((col, i) => {
    page.drawText(col, {
      x: colX + 5,
      y: tableTop,
      size: 10,
      font: helveticaBold,
      color: black,
    });
    colX += colWidths[i];
  });

  // -------------------------------------------------------------------------
  // TABLE ROWS
  // -------------------------------------------------------------------------

  let rowY = tableTop - 30;
  let subtotal = 0;

  for (const item of data.items) {
    const amount = item.quantity * item.unitPrice;
    subtotal += amount;

    colX = 50;

    // Description
    page.drawText(item.description, {
      x: colX + 5,
      y: rowY,
      size: 10,
      font: helvetica,
      color: black,
    });
    colX += colWidths[0];

    // Quantity
    page.drawText(item.quantity.toString(), {
      x: colX + 5,
      y: rowY,
      size: 10,
      font: helvetica,
      color: black,
    });
    colX += colWidths[1];

    // Unit Price
    page.drawText(`$${item.unitPrice.toFixed(2)}`, {
      x: colX + 5,
      y: rowY,
      size: 10,
      font: helvetica,
      color: black,
    });
    colX += colWidths[2];

    // Amount
    page.drawText(`$${amount.toFixed(2)}`, {
      x: colX + 5,
      y: rowY,
      size: 10,
      font: helvetica,
      color: black,
    });

    rowY -= 25;
  }

  // -------------------------------------------------------------------------
  // TOTALS
  // -------------------------------------------------------------------------

  const tax = subtotal * 0.1; // 10% tax
  const total = subtotal + tax;

  rowY -= 20;

  // Line
  page.drawLine({
    start: { x: width - 250, y: rowY + 15 },
    end: { x: width - 50, y: rowY + 15 },
    thickness: 1,
    color: rgb(0.8, 0.8, 0.8),
  });

  // Subtotal
  page.drawText('Subtotal:', {
    x: width - 200,
    y: rowY,
    size: 10,
    font: helvetica,
    color: gray,
  });
  page.drawText(`$${subtotal.toFixed(2)}`, {
    x: width - 100,
    y: rowY,
    size: 10,
    font: helvetica,
    color: black,
  });

  rowY -= 20;

  // Tax
  page.drawText('Tax (10%):', {
    x: width - 200,
    y: rowY,
    size: 10,
    font: helvetica,
    color: gray,
  });
  page.drawText(`$${tax.toFixed(2)}`, {
    x: width - 100,
    y: rowY,
    size: 10,
    font: helvetica,
    color: black,
  });

  rowY -= 25;

  // Total
  page.drawText('Total:', {
    x: width - 200,
    y: rowY,
    size: 14,
    font: helveticaBold,
    color: black,
  });
  page.drawText(`$${total.toFixed(2)}`, {
    x: width - 100,
    y: rowY,
    size: 14,
    font: helveticaBold,
    color: primary,
  });

  // -------------------------------------------------------------------------
  // FOOTER
  // -------------------------------------------------------------------------

  page.drawText('Thank you for your business!', {
    x: 50,
    y: 80,
    size: 12,
    font: helvetica,
    color: gray,
  });

  page.drawText('Payment due within 30 days.', {
    x: 50,
    y: 60,
    size: 10,
    font: helvetica,
    color: gray,
  });

  return await pdfDoc.save();
}

// =============================================================================
// EXPORT
// =============================================================================

export default app;

/**
 * wrangler.jsonc configuration:
 *
 * {
 *   "name": "invoice-generator",
 *   "main": "src/index.ts",
 *   "compatibility_date": "2024-01-01",
 *   "compatibility_flags": ["nodejs_compat"],
 *
 *   // Optional: For HTML→PDF with Browser Rendering (paid feature)
 *   "browser": {
 *     "binding": "BROWSER"
 *   }
 * }
 */
