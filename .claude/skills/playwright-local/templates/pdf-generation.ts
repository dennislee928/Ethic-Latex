/**
 * PDF Generation Template
 *
 * Convert web pages to PDFs:
 * - Custom margins and page size
 * - Background graphics
 * - Headers/footers
 * - Multiple pages to single PDF
 */

import { chromium } from 'playwright';
import path from 'path';

async function generatePDF(url: string, outputPath: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    console.log(`Loading ${url}...`);
    await page.goto(url, { waitUntil: 'networkidle' });

    console.log(`Generating PDF to ${outputPath}...`);
    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '1cm',
        right: '1cm',
        bottom: '1cm',
        left: '1cm',
      },
      // Optional: Add header/footer
      displayHeaderFooter: true,
      headerTemplate: `
        <div style="font-size: 10px; text-align: center; width: 100%;">
          <span>${url}</span>
        </div>
      `,
      footerTemplate: `
        <div style="font-size: 10px; text-align: center; width: 100%;">
          <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
        </div>
      `,
    });

    console.log('PDF generated successfully!');
  } catch (error) {
    console.error('PDF generation failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

async function generateMultiPagePDF(urls: string[], outputPath: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    console.log(`Generating multi-page PDF from ${urls.length} URLs...`);

    // Concatenate all pages into HTML
    let combinedHTML = '<html><body>';

    for (const url of urls) {
      console.log(`Loading ${url}...`);
      await page.goto(url, { waitUntil: 'networkidle' });

      const content = await page.content();
      combinedHTML += content + '<div style="page-break-after: always;"></div>';
    }

    combinedHTML += '</body></html>';

    // Set content and generate PDF
    await page.setContent(combinedHTML);

    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '1cm',
        right: '1cm',
        bottom: '1cm',
        left: '1cm',
      },
    });

    console.log(`Multi-page PDF generated: ${outputPath}`);
  } catch (error) {
    console.error('Multi-page PDF generation failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

// Single page: npx tsx pdf-generation.ts <url> <output.pdf>
// Multi-page: npx tsx pdf-generation.ts --multi <url1> <url2> ... <output.pdf>

const args = process.argv.slice(2);

if (args[0] === '--multi') {
  const urls = args.slice(1, -1);
  const outputPath = args[args.length - 1];
  generateMultiPagePDF(urls, outputPath);
} else {
  const url = args[0] || 'https://example.com';
  const outputPath = args[1] || './output.pdf';
  generatePDF(url, outputPath);
}
