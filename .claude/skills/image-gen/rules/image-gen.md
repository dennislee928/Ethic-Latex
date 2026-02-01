# Image Generation Rules

Correction rules for Gemini Native Image Generation.

## Model Selection

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| DALL-E for website images | Gemini 3 Image Generation (better text, editing) |
| Midjourney | Gemini 3 Image Generation (API access, editing) |
| `gemini-pro-vision` for generation | `gemini-3-flash-image-generation` |
| Generic model for 4K | `gemini-3-pro-image-generation` |

## API Configuration

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `generateImage()` method | `generateContent()` with `responseModalities: ["TEXT", "IMAGE"]` |
| Missing `responseModalities` | Always include `responseModalities: ["TEXT", "IMAGE"]` |
| `imageConfig` | `imageGenerationConfig` |
| `size: "1024x1024"` | `aspectRatio: "1:1"` (use aspect ratio, not pixel size) |

Correct config structure:

```typescript
const response = await ai.models.generateContent({
  model: "gemini-3-flash-image-generation",
  contents: prompt,
  config: {
    responseModalities: ["TEXT", "IMAGE"],
    imageGenerationConfig: {
      aspectRatio: "16:9",
      // imageSize: "2K", // Pro only
    },
  },
});
```

## Prompting

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Keyword lists | Descriptive narrative paragraph |
| "high quality, 4k, detailed" | Specific scene description with lighting |
| Generic "professional photo" | Specify: camera, lens, lighting, setting |
| Missing context | Include environment, time of day, atmosphere |

## Australian Imagery

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Generic power outlet | Australian Type I (angled prongs) |
| Yellow safety vest | Hi-vis orange/yellow Australian standard |
| Left-hand drive vehicle | Right-hand drive (Australian) |
| Generic architecture | Queenslander, Federation, or modern Australian |
| Imperial measurements | Metric signage |

## Text in Images

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Gemini 3 Flash for infographics | Gemini 3 Pro (better text legibility) |
| Long paragraphs in image | Short labels, headlines only |
| Small text | Large, bold text (minimum 24pt equivalent) |
| Decorative fonts | Clear sans-serif for legibility |

## Multi-Turn Editing

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Generate new image for each edit | Use chat/multi-turn for refinement |
| Restate full prompt on edit | Reference previous + state change only |
| Single-shot complex edits | Break into multiple turns |

Correct pattern:

```typescript
const chat = client.chats.create({ model: "...", config: { ... } });

// Turn 1: Generate
const response1 = await chat.send_message("Create a hero image...");

// Turn 2: Edit
const response2 = await chat.send_message("Change the vest color to green");

// Turn 3: Refine
const response3 = await chat.send_message("Widen the image to 21:9");
```

## Output Handling

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Assume single image output | Loop through all parts for images |
| Text-only response check | Check for `inlineData` in parts |
| Direct base64 to file | Decode: `Buffer.from(data, "base64")` |

## Limitations to Mention

- All images include SynthID watermark (invisible, for AI detection)
- Exact number of output images not guaranteed
- Flash model: up to 3 input images
- Pro model: up to 14 input images (5 high-fidelity objects, 5 humans)
- Best language support: EN, DE, ES, FR, JA, KO, PT, ZH
