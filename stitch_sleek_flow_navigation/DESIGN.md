---
name: Flysheep Aesthetic
colors:
  surface: '#fbf8ff'
  surface-dim: '#d7d8f4'
  surface-bright: '#fbf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f2ff'
  surface-container: '#edecff'
  surface-container-high: '#e6e6ff'
  surface-container-highest: '#e0e0fc'
  on-surface: '#181a2e'
  on-surface-variant: '#554245'
  inverse-surface: '#2d2f44'
  inverse-on-surface: '#f1efff'
  outline: '#887175'
  outline-variant: '#dbc0c4'
  surface-tint: '#a03b56'
  primary: '#a03b56'
  on-primary: '#ffffff'
  primary-container: '#ff85a1'
  on-primary-container: '#771b38'
  inverse-primary: '#ffb1c0'
  secondary: '#006780'
  on-secondary: '#ffffff'
  secondary-container: '#5ed8ff'
  on-secondary-container: '#005c72'
  tertiary: '#845400'
  on-tertiary: '#ffffff'
  tertiary-container: '#e49c31'
  on-tertiary-container: '#5a3800'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9df'
  primary-fixed-dim: '#ffb1c0'
  on-primary-fixed: '#3f0016'
  on-primary-fixed-variant: '#81233f'
  secondary-fixed: '#b7eaff'
  secondary-fixed-dim: '#5bd5fc'
  on-secondary-fixed: '#001f28'
  on-secondary-fixed-variant: '#004e61'
  tertiary-fixed: '#ffddb6'
  tertiary-fixed-dim: '#ffb95a'
  on-tertiary-fixed: '#2a1800'
  on-tertiary-fixed-variant: '#643f00'
  background: '#fbf8ff'
  on-background: '#181a2e'
  surface-variant: '#e0e0fc'
typography:
  display-lg:
    fontFamily: Quicksand
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Quicksand
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: Quicksand
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 24px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

This design system draws inspiration from high-fidelity anime interface design, specifically focusing on the "resource shelter" aesthetic: a blend of cozy, lived-in atmosphere and high-tech efficiency. The brand personality is **vibrant, energetic, and optimistic**, evoking the feeling of a modern social hub or a creative dashboard.

The visual style is a hybrid of **Glassmorphism** and **Soft-Industrialism**. It utilizes deeply blurred, semi-transparent surfaces to create a sense of light and air, contrasted by sharp, high-energy accents. The interface should feel like a digital collectible—precious, polished, and full of life. Subtle glow effects (outer glows) and floating particle elements provide a sense of constant, gentle motion.

## Colors

The palette is anchored by "Sakura Pink" (#FF85A1) as the primary brand color, used for critical actions and brand markers. "Electric Blue" (#4CC9F0) acts as the secondary accent, providing a cool, high-tech contrast that suggests energy and connectivity. "Sunset Orange" (#FFB347) is used sparingly for highlights, notifications, or "warm" interaction states.

**Backgrounds & Surfaces:**
- Use a soft, off-white or very pale lavender base for the global background.
- UI containers use a 60-80% translucent white with a heavy backdrop-blur (20px+) to achieve the frosted glass effect.
- Success states should lean toward a mint green, while errors use a vibrant, almost neon coral.

## Typography

The typography system relies on a contrast between **rounded friendliness** and **technical precision**. 

- **Quicksand** is the voice of the brand, used for large headlines and display text. Its rounded terminals mirror the "cute" and "approachable" anime aesthetic.
- **Plus Jakarta Sans** provides a clean, highly legible experience for body copy and long-form text, maintaining a soft but professional tone.
- **Space Grotesk** is used for UI labels, data points, and small navigational elements. Its sharp, geometric, and slightly "techy" nature balances the softness of the headlines, grounding the design in a modern UI context.

## Layout & Spacing

This design system utilizes a **fluid-to-fixed hybrid grid**. On desktop, content is contained within a 1280px max-width container to ensure readability, while the background particle effects bleed to the edges.

**Grid System:**
- **Desktop:** 12-column grid, 24px gutter, 40px side margins.
- **Tablet:** 8-column grid, 16px gutter, 24px side margins.
- **Mobile:** 4-column grid, 12px gutter, 16px side margins.

Spacing follows an 8px base unit. Use generous white space between major sections to let the glassmorphic background blurs "breathe." Content blocks should feel like floating islands rather than a rigid stack.

## Elevation & Depth

Depth is conveyed through **translucency and atmospheric blurs** rather than traditional black shadows.

1.  **Base Layer:** Solid color or soft gradient background with particle assets.
2.  **Surface Layer (Level 1):** 60% opacity white with `backdrop-filter: blur(24px)`. Thin 1px semi-transparent white border to define the edge.
3.  **Raised Layer (Level 2):** Same as Level 1, but with a soft "glow" shadow (using the primary or secondary color at 10-15% opacity) instead of a dark shadow.
4.  **Active/Hover States:** Elements should slightly scale up (1.02x) and increase their glow intensity to appear "magnetic."

Avoid dark, heavy drop shadows; they muddy the vibrant anime colors. Use white inner glows to simulate light hitting the edges of the "glass" panels.

## Shapes

The shape language is dominated by **large radii and pill-shaped elements**. 

- **Standard Containers:** Use 1rem (16px) or 1.5rem (24px) for large cards.
- **Interactive Elements:** Buttons and tags should be fully pill-shaped (rounded-full) to maximize the "squishy" and playful feel.
- **Icons:** Should feature rounded ends and consistent stroke weights (2px).
- **Mascot Frames:** Use "blob" shapes or organic, irregular circles for avatar frames or mascot backgrounds to break the grid's rigidity.

## Components

**Buttons:**
- **Primary:** Pill-shaped, gradient fill (Primary to Secondary), with a subtle white drop shadow and a "glow" on hover.
- **Secondary:** Frosted glass background with a colored 2px border.

**Input Fields:**
- Fully rounded corners. Background should be a slightly darker translucency than the card it sits on. On focus, the border glows with the Electric Blue accent.

**Chips/Tags:**
- Small, pill-shaped, using high-contrast colors (Sakura Pink or Sunset Orange) with white text. Use them for categories or status indicators.

**Cards:**
- Heavy backdrop-blur. 1px white border. Inside the card, include a "glass highlight"—a very thin, subtle linear gradient at the top to simulate light reflecting off a glass edge.

**Mascots & Particles:**
- Integrate "Helper" mascots in corner areas of major views. Use "Floating Particles" (small circles or spark shapes) in the background with a CSS parallax effect to create depth as the user scrolls.