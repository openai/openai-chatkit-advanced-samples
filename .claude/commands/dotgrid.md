---
description: Generate Humorist-style dot grid icons from text prompts
---

# Dot Grid Icon Generator

You are generating a dot grid icon in the Humorist style through **3 drafts**.

## Your Task

Create a dot grid icon for: **$ARGUMENTS**

## Resolution

Parse the user's input to detect resolution:
- `low` or `8x8` → 8x8 grid (bold, minimal, ultra-iconic)
- `medium` or `16x16` or no specification → 16x16 grid (default, balanced)
- `high` or `32x32` → 32x32 grid (detailed, expressive)

**Important**: Higher resolution means more dots to work with - reimagine the design to take advantage of finer detail, smoother curves, and better use of negative space. Don't just scale up the lower resolution version.

## Strict Rules

- Every cell is either `off` or exactly one color from the palette
- NO gradients, NO shading, NO transparency variations
- Background is always `off` - only show the subject
- Be creative with shape, form, and color choices

## Color Palette

- `off` - no dot (transparent)
- `text` - dark gray #464646
- `red` - #D74E39
- `orange` - #DA6800
- `yellow` - #FFC922
- `pink` - #E7B5A0
- `green` - #8AA47D
- `blue` - #6CC2FF
- `purple` - #9B85B7

## Three-Draft Process

### Draft 1: First Attempt
1. Visualize the essential shape at the chosen resolution
2. Generate JSON and render it
3. View the PNG output
4. Critique: Is it recognizable? What's missing?

### Draft 2: Refinement
1. Based on your critique, improve the design
2. Fix proportions, add details, adjust colors
3. Generate JSON and render it
4. View the PNG output
5. Critique: Better? What else?

### Draft 3: Final Polish
1. Final improvements for clarity and character
2. Make it iconic and fun
3. Generate JSON and render it
4. Present the final result

## JSON Format

```json
{
  "grid": [
    ["off", "off", "red", "red", ...],
    ...
  ],
  "name": "heart-medium-draft1"
}
```

Grid dimensions must match: 8x8, 16x16, or 32x32.

Use naming: `{subject}-{resolution}-draft1`, `{subject}-{resolution}-draft2`, `{subject}-{resolution}-final`

## Execution

For each draft, write JSON to a temp file and run:

```bash
uv run specs/humorist/src/dotgrid.py --file /tmp/dotgrid_temp.json
```

Then use the Read tool to view the PNG at `specs/humorist/output/{name}.png` and critique it before the next draft.

## Now Begin

Create **$ARGUMENTS** through 3 iterative drafts.
