# CUPID Font Definitions

Extracted from Figma design system.

## Font Family: Lexend

The design system uses the **Lexend** superfamily - a variable font designed for improved reading proficiency. Multiple widths are used for hierarchy.

### Google Fonts Import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lexend+Giga:wght@400;600;900&family=Lexend+Peta:wght@700&family=Lexend:wght@300;400;500&display=swap" rel="stylesheet">
```

---

## Type Scale

### Display / Logo
| Property | Value |
|----------|-------|
| Font | Lexend Giga |
| Weight | Regular (400) |
| Size | 64px |
| Color | `#000000` (black) |
| Usage | Page titles, hero text |

```css
.display {
    font-family: 'Lexend Giga', sans-serif;
    font-weight: 400;
    font-size: 64px;
    color: #000000;
}
```

---

### Nav / Brand
| Property | Value |
|----------|-------|
| Font | Lexend Giga |
| Weight | Black (900) |
| Size | 16px |
| Color | `#000000` (black) |
| Usage | Navigation brand name |

```css
.nav-brand {
    font-family: 'Lexend Giga', sans-serif;
    font-weight: 900;
    font-size: 16px;
    color: #000000;
}
```

---

### Header 1
| Property | Value |
|----------|-------|
| Font | Lexend Giga |
| Weight | SemiBold (600) |
| Size | 42px |
| Color | `#657B83` (muted text) |
| Usage | Section headers, primary headings |

```css
.h1 {
    font-family: 'Lexend Giga', sans-serif;
    font-weight: 600;
    font-size: 42px;
    color: #657B83;
}
```

---

### Header 2 / Header 3
| Property | Value |
|----------|-------|
| Font | Lexend Giga |
| Weight | SemiBold (600) |
| Size | 32px |
| Color | `#657B83` (muted text) |
| Usage | Subsection headers |

```css
.h2, .h3 {
    font-family: 'Lexend Giga', sans-serif;
    font-weight: 600;
    font-size: 32px;
    color: #657B83;
}
```

---

### Block Quote / Emphasis
| Property | Value |
|----------|-------|
| Font | Lexend Peta |
| Weight | Bold (700) |
| Size | 20px |
| Color | `#000000` (black) |
| Usage | Pull quotes, emphasized text, callouts |

```css
.blockquote {
    font-family: 'Lexend Peta', sans-serif;
    font-weight: 700;
    font-size: 20px;
    color: #000000;
}
```

---

### Body
| Property | Value |
|----------|-------|
| Font | Lexend |
| Weight | Light (300) |
| Size | 24px |
| Color | `#000000` (black) |
| Usage | Body text, paragraphs |

```css
.body {
    font-family: 'Lexend', sans-serif;
    font-weight: 300;
    font-size: 24px;
    color: #000000;
}
```

---

## CSS Custom Properties

```css
:root {
    /* Font Families */
    --font-display: 'Lexend Giga', sans-serif;
    --font-emphasis: 'Lexend Peta', sans-serif;
    --font-body: 'Lexend', sans-serif;

    /* Font Weights */
    --weight-light: 300;
    --weight-regular: 400;
    --weight-medium: 500;
    --weight-semibold: 600;
    --weight-bold: 700;
    --weight-black: 900;

    /* Font Sizes */
    --size-display: 64px;
    --size-h1: 42px;
    --size-h2: 32px;
    --size-h3: 32px;
    --size-body: 24px;
    --size-blockquote: 20px;
    --size-nav: 16px;

    /* Text Colors */
    --text-primary: #000000;
    --text-secondary: #657B83;
    --text-muted: #93A1A1;
}
```

---

## Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        'display': ['"Lexend Giga"', 'sans-serif'],
        'emphasis': ['"Lexend Peta"', 'sans-serif'],
        'body': ['Lexend', 'sans-serif'],
      },
      fontSize: {
        'display': ['64px', { lineHeight: '1.1' }],
        'h1': ['42px', { lineHeight: '1.2' }],
        'h2': ['32px', { lineHeight: '1.3' }],
        'h3': ['32px', { lineHeight: '1.3' }],
        'body': ['24px', { lineHeight: '1.5' }],
        'blockquote': ['20px', { lineHeight: '1.4' }],
        'nav': ['16px', { lineHeight: '1' }],
      }
    }
  }
}
```

---

## Typography Hierarchy Summary

| Role | Font | Weight | Size | Color |
|------|------|--------|------|-------|
| Display | Lexend Giga | 400 | 64px | Black |
| Nav Brand | Lexend Giga | 900 | 16px | Black |
| H1 | Lexend Giga | 600 | 42px | #657B83 |
| H2/H3 | Lexend Giga | 600 | 32px | #657B83 |
| Blockquote | Lexend Peta | 700 | 20px | Black |
| Body | Lexend | 300 | 24px | Black |

---

## Usage Guidelines

1. **Lexend Giga** (wide) - Use for display text, headings, and navigation. The extra width commands attention.

2. **Lexend Peta** (extra wide) - Reserve for block quotes and special emphasis. Use sparingly for maximum impact.

3. **Lexend** (standard) - Primary body text. Light weight (300) keeps it readable at larger sizes.

4. **Color hierarchy**: Black for primary content, `#657B83` for secondary headers to create visual depth.

5. **Spacing**: The wide letterforms of Lexend Giga need generous line-height and padding.
