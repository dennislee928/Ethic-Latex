# Image Editing

Gemini can edit existing images with precise control.

## Edit Capabilities

| Operation | Example Prompt |
|-----------|----------------|
| Colour change | "Change the hi-vis vest from orange to lime green" |
| Add element | "Add a flock of pelicans flying in the sky" |
| Remove element | "Remove the logo from the uniform" |
| Text change | "Change the title from 'How We Work' to 'Our Process'" |
| Widen/extend | "Extend this image to the left, showing more kitchen" |
| Style transfer | "Transform this into a watercolor painting style" |
| Background change | "Replace the background with a modern office" |

## API Pattern

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

async function editImage(imagePath: string, editPrompt: string, aspectRatio?: string) {
  const imageBuffer = fs.readFileSync(imagePath);
  const base64Image = imageBuffer.toString('base64');
  const mimeType = imagePath.endsWith('.png') ? 'image/png' : 'image/jpeg';

  const config: any = {
    responseModalities: ["TEXT", "IMAGE"],
  };
  if (aspectRatio) {
    config.imageGenerationConfig = { aspectRatio };
  }

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-image-generation",
    contents: [
      {
        role: "user",
        parts: [
          {
            inlineData: {
              mimeType,
              data: base64Image,
            },
          },
          { text: editPrompt },
        ],
      },
    ],
    config,
  });

  // Extract result
  for (const part of response.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData) {
      return Buffer.from(part.inlineData.data, 'base64');
    }
  }
}
```

## Widen/Extend (Outpainting)

Change aspect ratio while extending the scene:

```typescript
// Original 16:9 → ultrawide 21:9
const widened = await editImage(
  "hero.png",
  "Extend this image to show more of the scene on both sides. Maintain style and lighting.",
  "21:9"
);
```

## Style Transfer

Apply artistic styles while keeping composition:

```typescript
const watercolor = await editImage(
  "hero.png",
  "Transform this into a watercolor painting style while keeping the same scene"
);
```

## Multi-Turn Editing (Chat)

For complex edits, use chat context to build on previous results:

```typescript
const chat = await ai.chats.create({
  model: "gemini-3-flash-image-generation",
  config: { responseModalities: ['TEXT', 'IMAGE'] }
});

// Turn 1: Generate base
let response = await chat.sendMessage("Create a hero image for a plumber website...");

// Turn 2: Refine
response = await chat.sendMessage("Change the vest to lime green");

// Turn 3: Adjust
response = await chat.sendMessage("Add more tools on the counter");

// Turn 4: Final
response = await chat.sendMessage("Widen to 21:9 aspect ratio");
```

## Tips

- Be specific: "Change X to Y" works better than "modify X"
- Specify what to KEEP: "Keep everything else the same"
- For text edits, include exact old and new text
- For colour changes, use colour names or hex codes
- For outpainting, specify direction: "extend to the left"
