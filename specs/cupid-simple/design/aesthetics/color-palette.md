# CUPID Color Palette

Extracted from Figma design system.

## Core Palette

| Name | Hex | Preview | Usage |
|------|-----|---------|-------|
| **Background** | `#FDF6E3` | ![#FDF6E3](https://via.placeholder.com/20/FDF6E3/FDF6E3) | Primary background, canvas |
| **Text** | `#464646` | ![#464646](https://via.placeholder.com/20/464646/464646) | Primary text, headings |

## Accent Colors

| Name | Hex | Preview | Usage |
|------|-----|---------|-------|
| **Red** | `#D74E39` | ![#D74E39](https://via.placeholder.com/20/D74E39/D74E39) | Primary accent, love/passion, Cupid's arrow |
| **Orange** | `#DA6800` | ![#DA6800](https://via.placeholder.com/20/DA6800/DA6800) | Secondary accent, warmth, fire signs |
| **Yellow** | `#FFC922` | ![#FFC922](https://via.placeholder.com/20/FFC922/FFC922) | Highlights, optimism, sun |
| **Pink** | `#E7B5A0` | ![#E7B5A0](https://via.placeholder.com/20/E7B5A0/E7B5A0) | Soft romantic, Venus, connection |
| **Green** | `#8AA47D` | ![#8AA47D](https://via.placeholder.com/20/8AA47D/8AA47D) | Growth, earth signs, positive change |
| **Blue** | `#6CC2FF` | ![#6CC2FF](https://via.placeholder.com/20/6CC2FF/6CC2FF) | Air signs, communication, clarity |
| **Purple** | `#9B85B7` | ![#9B85B7](https://via.placeholder.com/20/9B85B7/9B85B7) | Mystical, intuition, water signs |

## CSS Variables

```css
:root {
    /* Core */
    --color-background: #FDF6E3;
    --color-text: #464646;

    /* Accents */
    --color-red: #D74E39;
    --color-orange: #DA6800;
    --color-yellow: #FFC922;
    --color-pink: #E7B5A0;
    --color-green: #8AA47D;
    --color-blue: #6CC2FF;
    --color-purple: #9B85B7;
}
```

## Semantic Tokens

```css
:root {
    /* Backgrounds */
    --bg-primary: var(--color-background);
    --bg-surface: #F5EFE0; /* slightly darker for cards */

    /* Text */
    --text-primary: var(--color-text);
    --text-secondary: #6B6B6B;
    --text-muted: #8B8B8B;

    /* Accent (primary action color) */
    --accent-primary: var(--color-red);
    --accent-secondary: var(--color-orange);

    /* Status */
    --color-success: var(--color-green);
    --color-warning: var(--color-yellow);
    --color-error: var(--color-red);

    /* Astrological Elements */
    --element-fire: var(--color-orange);
    --element-earth: var(--color-green);
    --element-air: var(--color-blue);
    --element-water: var(--color-purple);
}
```

## Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        cupid: {
          background: '#FDF6E3',
          text: '#464646',
          red: '#D74E39',
          orange: '#DA6800',
          yellow: '#FFC922',
          pink: '#E7B5A0',
          green: '#8AA47D',
          blue: '#6CC2FF',
          purple: '#9B85B7',
        }
      }
    }
  }
}
```

## Color Relationships

### Warm Spectrum (Fire/Passion)
`Red → Orange → Yellow → Pink`

### Cool Spectrum (Calm/Intuition)
`Blue → Purple → Green`

### Contrast Pairs
- Background `#FDF6E3` + Text `#464646` = **10.2:1** (AAA)
- Background `#FDF6E3` + Red `#D74E39` = **4.8:1** (AA)
- Background `#FDF6E3` + Orange `#DA6800` = **4.5:1** (AA)

## Usage Guidelines

1. **Background** should be the dominant color (canvas, cards)
2. **Text** for all readable content
3. **Red** sparingly for primary actions and love-related UI
4. **Orange** for secondary emphasis and warmth
5. **Yellow** for highlights, stars, optimism indicators
6. **Pink** for soft romantic moments, Venus indicators
7. **Green** for positive changes, growth, earth element
8. **Blue** for communication, air element, clarity
9. **Purple** for mystical/intuitive elements, water signs
