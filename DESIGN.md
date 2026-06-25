---
name: Vibrant Zenith
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e2bfb0'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#a98a7d'
  outline-variant: '#5a4136'
  surface-tint: '#ffb693'
  primary: '#ffb693'
  on-primary: '#561f00'
  primary-container: '#ff6b00'
  on-primary-container: '#572000'
  inverse-primary: '#a04100'
  secondary: '#d3fbff'
  on-secondary: '#00363a'
  secondary-container: '#00eefc'
  on-secondary-container: '#00686f'
  tertiary: '#e5b4ff'
  on-tertiary: '#4f0077'
  tertiary-container: '#ca72ff'
  on-tertiary-container: '#500079'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbcc'
  primary-fixed-dim: '#ffb693'
  on-primary-fixed: '#351000'
  on-primary-fixed-variant: '#7a3000'
  secondary-fixed: '#7df4ff'
  secondary-fixed-dim: '#00dbe9'
  on-secondary-fixed: '#002022'
  on-secondary-fixed-variant: '#004f54'
  tertiary-fixed: '#f5d9ff'
  tertiary-fixed-dim: '#e5b4ff'
  on-tertiary-fixed: '#30004b'
  on-tertiary-fixed-variant: '#7000a7'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-xl:
    fontFamily: Sora
    fontSize: 64px
    fontWeight: '800'
    lineHeight: 72px
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Sora
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-md:
    fontFamily: Sora
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 48px
  margin-mobile: 16px
  container-max: 1440px
---

## Brand & Style
This design system reimagines executive efficiency for a digital-native generation. It moves away from traditional corporate rigidity toward a "Techno-Optimist" aesthetic—mixing the high-performance utility of a professional suite with the high-energy visual language of contemporary street culture and gaming interfaces.

The design style is a hybrid of **Glassmorphism** and **High-Contrast Bold**. It utilizes deep, saturated dark surfaces as a canvas for vibrant, glowing accents and razor-sharp typography. The emotional response is one of urgency, confidence, and cutting-edge capability. It feels less like a desk and more like a cockpit.

## Colors
The palette is anchored by a high-octane **Vibrant Orange (#FF6B00)**, used as the primary signal color for calls to action and critical data points. This is supported by an "Electric Cyan" secondary and "Cyber Purple" tertiary color to provide a neon-inflected spectrum for data visualization and state changes.

The background architecture uses a tiered dark system:
- **Base:** #080808 (The void)
- **Surface:** #121212 (The main container level)
- **Elevated:** #1E1E1E (Interactive layers)

Accents utilize a "glow" logic, where primary elements emit a soft #FF6B00 outer shadow to simulate light emission against the dark backdrop.

## Typography
The typographic scale is aggressive and highly structured. **Sora** provides a geometric, futuristic weight for headlines, emphasizing a tech-forward personality with its distinctive counters and wide stance. 

**Hanken Grotesk** serves as the workhorse for body content, offering professional clarity with a modern, sharp finish. **JetBrains Mono** is utilized for labels, metadata, and secondary actions to lean into the "technical/developer" aesthetic that resonates with Gen Z's appreciation for brutalist and functional UI. Use uppercase styling for labels to maximize the industrial feel.

## Layout & Spacing
The layout follows a **Fluid Grid** model with high-density information mapping. We use a 12-column grid for desktop and a 4-column grid for mobile. 

Spacing is tight and systematic, based on a 4px base unit to allow for high-precision alignment. Large margins are used on the outer edges of the viewport to "frame" the content like a premium magazine or a dashboard. Internal gutters remain generous (24px) to prevent the high-contrast elements from feeling cluttered. Content should reflow vertically on mobile, with horizontal scrolling reserved strictly for data tables or chip-based filtering.

## Elevation & Depth
Depth is created through **Glassmorphism** and light-based layering rather than traditional shadows.
- **Layers:** Use semi-transparent backgrounds (e.g., `rgba(30, 30, 30, 0.6)`) with a `backdrop-filter: blur(20px)`.
- **Borders:** Instead of heavy shadows, use thin (1px) inner borders with a slight gradient (top-left to bottom-right) to simulate a light source catching the edge of a glass pane.
- **Glows:** Active or "focused" elements should use an outer glow (`box-shadow: 0 0 15px rgba(255, 107, 0, 0.3)`) to create a sense of energy and importance.
- **Z-Index Hierarchy:** Higher elevation layers become progressively lighter and less transparent.

## Shapes
The shape language is "Squircular"—blending organic smoothness with geometric precision. A consistent 0.5rem (8px) corner radius is applied to standard components to maintain a friendly but professional feel. 

Interactive elements like buttons and input fields use a slightly more pronounced rounding, while large containers and sections may use sharper corners to emphasize the structural integrity of the layout. Avoid full pill shapes except for status tags or "Live" indicators to keep the aesthetic feeling modern and architectural rather than bubbly.

## Components
- **Buttons:** Primary buttons are solid #FF6B00 with black text for maximum contrast. Secondary buttons use the "Ghost" style: a transparent body with a 1px orange border and an orange glow on hover.
- **Chips:** Small, monochromatic tags using JetBrains Mono. Use subtle background tints (e.g., 10% opacity of the primary color).
- **Cards:** The core container. Must feature the glassmorphic blur and a subtle 1px border. Background should be #1E1E1E at 80% opacity.
- **Inputs:** Dark backgrounds (#080808) with a bottom-only border that "activates" by expanding into a full orange outline when focused.
- **Lists:** Use high-contrast dividers (1px, 10% white) and hover states that utilize a subtle horizontal slide animation.
- **Glow Indicators:** Use small, pulsing circular dots for "live" or "online" statuses to add motion to the static UI.