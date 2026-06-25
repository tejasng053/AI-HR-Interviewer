---
name: Executive Zenith
colors:
  surface: '#0f131c'
  surface-dim: '#0f131c'
  surface-bright: '#353943'
  surface-container-lowest: '#0a0e17'
  surface-container-low: '#181b25'
  surface-container: '#1c1f29'
  surface-container-high: '#262a34'
  surface-container-highest: '#31353f'
  on-surface: '#dfe2ef'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dfe2ef'
  inverse-on-surface: '#2c303a'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#ffc640'
  on-secondary: '#402d00'
  secondary-container: '#e3aa00'
  on-secondary-container: '#5a4100'
  tertiary: '#ffb3ad'
  on-tertiary: '#68000a'
  tertiary-container: '#ff5451'
  on-tertiary-container: '#5c0008'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#ffdf9f'
  secondary-fixed-dim: '#f9bd22'
  on-secondary-fixed: '#261a00'
  on-secondary-fixed-variant: '#5c4300'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#0f131c'
  on-background: '#dfe2ef'
  surface-variant: '#31353f'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
  container-max: 1200px
---

## Brand & Style

The design system is crafted for high-stakes enterprise environments where precision and authority are paramount. It targets a professional demographic—HR executives and high-level candidates—evoking an atmosphere of serious, focused, and secure interaction.

The aesthetic leans into a **Modern Corporate** style with **Glassmorphic** accents. It balances the "Cold" efficiency of AI with the "Warmth" of premium editorial design. By utilizing deep navy backgrounds and translucent layers, the UI feels expansive yet structured, providing a focused "stage" for the interview process. The emotional response is one of calm confidence, reliability, and technological sophistication.

## Colors

The palette is built on a "Classic Dark" foundation to reduce eye strain during long interview sessions while maintaining a premium aesthetic.

- **Primary Canvas:** A deep, obsidian navy (#0a0e17) serves as the base, providing maximum contrast for typography.
- **Accents:** 
    - **Primary Blue (#3b82f6):** Reserved for primary actions (e.g., "Start Interview," "Submit Response").
    - **Accent Gold (#fbbf24):** Used sparingly for critical status updates, timers, and warning states to ensure they grab attention without inducing panic.
    - **Accent Red (#ef4444):** Exclusively used for recording indicators and destructive actions, providing a clear visual "Live" signal.
- **Glassmorphism:** Surfaces utilize semi-transparent hex codes with background blurs to create a sense of physical layering.

## Typography

This design system prioritizes legibility and clarity above all else, utilizing **Inter** for its systematic and neutral character. 

The type hierarchy is strictly enforced to guide the candidate through the interview flow. High-contrast white text (#f8fafc) is used for headings to ensure they are immediately scannable against the dark background. Body text uses a slightly softened slate (#94a3b8) to prevent "vibration" and improve long-form reading comfort. Functional labels (like "Time Remaining") use increased letter spacing and uppercase styling to distinguish them from conversational content.

## Layout & Spacing

The layout philosophy follows a **Fixed Grid** model for desktop to maintain a professional, centered "stage" feel, while transitioning to a **Fluid Grid** on mobile.

- **Desktop:** A 12-column grid with a maximum container width of 1200px. This prevents line lengths from becoming too long, which is critical for reading interview questions.
- **Rhythm:** An 8px linear scale is used for all component-level spacing (padding, margins), while a 4px unit is used for fine-tuning icons and labels.
- **Reflow:** On mobile devices, sidebars collapse into bottom sheets or drawer menus to keep the video feed or question text as the primary focus.

## Elevation & Depth

Visual hierarchy is established through **Tonal Layering** combined with **Ambient Shadows**. Instead of relying purely on darkness, depth is suggested by "lifting" elements toward the user through color and transparency.

- **Base Layer:** The canvas (#0a0e17).
- **Surface Layer:** Cards and containers use #111827 with a subtle 1px inner border of white at 5% opacity to define the edge.
- **Elevated/Glass Layer:** Modals and dropdowns use a backdrop-filter blur (12px) and a semi-transparent background.
- **Shadows:** Shadows are extra-diffused and low-opacity (rgba(0,0,0,0.4)), using a larger blur radius (24px) to suggest a soft, natural lift rather than a harsh drop.

## Shapes

The design system employs a **Soft** shape language. This choice strikes a balance between the friendliness required for a comfortable interview and the structural rigor expected from a corporate HR tool.

- **Standard Elements:** Buttons and input fields use a 0.25rem (4px) radius.
- **Container Elements:** Cards and main panels use 0.5rem (8px) to soften the overall interface.
- **Indicators:** The recording "dot" and specific status badges use a full circle/pill shape to distinguish them as active system states.

## Components

### Buttons
Primary buttons use the Primary Blue (#3b82f6) with a subtle "morphing" gradient that shifts slightly on hover. Text is bold and centered. Secondary buttons use a ghost style with a 1px border.

### Interview Cards
The central component of the app. These feature a glassmorphic background with a 12px blur. On hover, a subtle CSS transform (scale 1.01) creates a tactile, parallax effect to indicate focus.

### Input Fields
Inputs are dark-filled (#0f172a) with a subtle border. On focus, the border glows with the Primary Blue and a subtle outer glow (4px spread).

### Recording Indicator
A dedicated component in the top-right corner. It features the Accent Red (#ef4444) with a soft pulsing animation to provide constant, non-intrusive feedback that audio/video is live.

### Progress & Timers
The Accent Gold (#fbbf24) is used for thin progress bars at the top of cards or circular countdown timers. This ensures the user is aware of time constraints without the color feeling as aggressive as red.