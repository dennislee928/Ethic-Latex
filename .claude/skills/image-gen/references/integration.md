# API Integration

## Installation

```bash
pnpm add @google/genai
```

**CRITICAL**: Use `@google/genai` NOT deprecated `@google/generative-ai`.

## TypeScript

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

async function generateImage(prompt: string, options: {
  aspectRatio?: string;
  imageSize?: "1K" | "2K" | "4K";
} = {}) {
  const { aspectRatio = "16:9", imageSize } = options;

  const config: any = {
    responseModalities: ["TEXT", "IMAGE"],
    imageGenerationConfig: { aspectRatio },
  };

  // imageSize only works with Pro model
  if (imageSize) {
    config.imageGenerationConfig.imageSize = imageSize;
  }

  const response = await ai.models.generateContent({
    model: imageSize
      ? "gemini-3-pro-image-generation"
      : "gemini-3-flash-image-generation",
    contents: prompt,
    config,
  });

  for (const part of response.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData) {
      return Buffer.from(part.inlineData.data, "base64");
    }
  }
}

// Usage
const hero = await generateImage(
  "Professional Australian plumber in modern home...",
  { aspectRatio: "16:9", imageSize: "4K" }
);
fs.writeFileSync("hero.png", hero);
```

## REST API (curl)

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-image-generation:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "A professional plumber at work..."}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageGenerationConfig": {"aspectRatio": "16:9"}
    }
  }' | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data' | base64 --decode > hero.png
```

## Post-Processing

### Background Removal (for transparency)

Gemini doesn't output transparent PNGs. Use rembg for background removal:

```bash
pip install rembg
rembg i hero.png hero-transparent.png
```

Or in Node.js with sharp + @imgly/background-removal:

```typescript
import { removeBackground } from "@imgly/background-removal-node";
import * as fs from "node:fs";

async function removeImageBackground(inputPath: string, outputPath: string) {
  const input = fs.readFileSync(inputPath);
  const blob = new Blob([input], { type: "image/png" });

  const result = await removeBackground(blob);
  const buffer = Buffer.from(await result.arrayBuffer());

  fs.writeFileSync(outputPath, buffer);
}
```

### WebP Conversion

```bash
cwebp -q 85 hero.png -o hero.webp
```

### Responsive Sizes

```bash
# Generate responsive image set
for size in 1920 1200 800; do
  magick hero.png -resize ${size}x hero-${size}.jpg
  cwebp -q 85 hero-${size}.jpg -o hero-${size}.webp
done
```

## File Organization

```
assets/
├── generated/
│   ├── hero/
│   │   ├── hero-4k.png        # Original 4K
│   │   ├── hero-1920.webp     # Desktop
│   │   ├── hero-1200.webp     # Tablet
│   │   ├── hero-800.webp      # Mobile
│   │   └── prompt.txt         # Generation prompt
│   ├── services/
│   └── infographics/
```

## Rate Limits

| Tier | Limit |
|------|-------|
| Free | 60 RPM |
| Pay-as-you-go | Higher limits |

## Notes

- All images include SynthID watermark (invisible)
- 4K images at highest quality are practically flawless
- Save prompts alongside images for regeneration
- Pro model recommended for text in images
