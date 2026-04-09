# Design System: The Cinematic Intelligence Framework

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Digital Observatory."** 

This is not a dashboard; it is a high-fidelity lens into the frontier of artificial intelligence. To move beyond the "standard dashboard" aesthetic, we utilize a **Non-Linear Layering** approach. This system rejects rigid, boxed-in layouts in favor of intentional asymmetry and "infinite depth." By leveraging glassmorphism and light-emissive accents, we create a UI that feels like a holographic projection—lightweight, sophisticated, and technically superior. 

The goal is to provide a sense of "Controlled Chaos," where data flows through a structured grid but is punctuated by vibrant neon "pulses" that draw the eye to critical research insights.

---

## 2. Colors & Atmospheric Depth
Our palette is rooted in the void, using light not just as a highlight, but as a functional material.

### The Palette
*   **Primary (Neon Blue):** `#00f2ff` — Used for active data streams and primary research actions.
*   **Secondary (Deep Purple):** `#8a2be2` — Used for secondary insights and exploratory paths.
*   **Tertiary (Vibrant Red):** `#ff3131` — Reserved exclusively for contradictions, system errors, or high-priority alerts.
*   **Surface Base:** `#111319` — The deep navy/black "dark matter" that grounds the experience.

### The "No-Line" Rule
Traditional 1px solid borders are strictly prohibited for sectioning. Structural separation must be achieved through:
1.  **Background Shifts:** Moving from `surface-container-low` to `surface-container-high`.
2.  **Glow-Based Edges:** Using a subtle `0.5px` outer glow or a highly transparent "Ghost Border" (10-20% opacity) to define the edge of a glass pane.

### Surface Hierarchy & Nesting
Treat the interface as a series of nested frosted glass panes. 
*   **Base Layer:** `surface` (The deep void).
*   **Content Sections:** `surface-container-low` with a 20px `backdrop-blur`.
*   **Floating Modals/Cards:** `surface-container-highest` with a `primary` neon-glow border.

### The "Glass & Gradient" Rule
Main CTAs and Hero sections must never be flat. Use a linear gradient (`primary` to `primary-container`) with a `15%` inner glow. This provides the "visual soul" required for a premium, futuristic feel.

---

## 3. Typography: Technical Authority
We pair the geometric precision of **Space Grotesk** with the humanist clarity of **Inter** and **Manrope**.

*   **Display & Headlines (Space Grotesk):** These are your "Technical Markers." The wide apertures and geometric forms convey a sense of futuristic engineering. Use `display-lg` for hero data points and `headline-md` for section titles.
*   **Body (Inter):** The workhorse. Inter is used for all research abstracts, documentation, and data descriptions. It ensures that even in a dark, neon-heavy environment, legibility remains absolute.
*   **Labels (Manrope):** Used for metadata, timestamps, and micro-copy. Manrope's slightly more condensed nature allows for dense data visualization without feeling cluttered.

---

## 4. Elevation & Depth: Tonal Layering
In this design system, height is indicated by light and blur, not just shadows.

*   **The Layering Principle:** To lift a research card, do not add a black shadow. Instead, increase the `backdrop-blur` and shift the background from `surface-container-lowest` to `surface-container-low`.
*   **Ambient Shadows:** If a floating element requires a shadow, use a tinted shadow: `rgba(0, 242, 255, 0.08)` (a Primary-tinted glow). This mimics the way neon light interacts with a physical surface.
*   **The Ghost Border:** For accessibility, use the `outline-variant` token at `15%` opacity. This creates a "razor-thin" technical edge that feels like a laser-cut boundary rather than a drawn line.
*   **Glassmorphism:** All "above-surface" components must use a semi-transparent surface color (`rgba(17, 19, 25, 0.7)`) to allow the underlying data patterns and grids to bleed through.

---

## 5. Components

### Buttons
*   **Primary:** High-gloss gradient (`primary` to `primary_container`). Border-radius: `md` (0.375rem). Text should be `on_primary` (Deep Navy). 
*   **Secondary:** Ghost style. Transparent fill with a `secondary` (Purple) ghost border. On hover, a subtle `0.15` opacity purple glow fills the container.
*   **Tertiary:** No background. Text-only with a trailing `->` icon, using the `primary` color.

### Chips (Data Tags)
*   **Research Chips:** `surface-container-highest` background with a `sm` radius. A tiny 4px neon dot indicates the status (Active/Static/Error).

### Input Fields
*   **Focus State:** The standard border-bottom glows `primary` (#00f2ff). The background shifts to a slightly brighter `surface_bright` to indicate "Active Entry."
*   **Error State:** Border-bottom glows `tertiary` (Red). Helper text uses `label-sm`.

### Cards & Lists
*   **Zero-Divider Policy:** Never use horizontal lines to separate list items. Use vertical spacing (16px–24px) or a alternating subtle background shift between `surface-container-low` and `surface-container-lowest`.
*   **Research Cards:** Must feature a "Technical Header"—a tiny `label-sm` text string in the top right corner indicating a serial number or timestamp, reinforcing the platform's research-heavy nature.

### Specialized Component: The "Pulse" Indicator
*   A small, animated concentric circle using the `primary` color. Used to indicate real-time data streaming or active AI processing.

---

## 6. Do's and Don'ts

### Do:
*   **Embrace Asymmetry:** Align the main research feed to a 12-column grid, but allow data visualizations to break the margins.
*   **Use Subtle Grids:** Apply a `10%` opacity dot-grid pattern to the background of `surface` to ground the UI elements.
*   **Prioritize Breathing Room:** With dark themes and neon borders, white space (or "dark space") is the only thing preventing visual fatigue.

### Don't:
*   **Don't use 100% White:** Never use `#FFFFFF` for text. Use `on_surface` (`#e2e2eb`) to reduce glare against the dark background.
*   **Don't Over-Glow:** If every element has a neon glow, nothing is important. Reserve glows for active states, primary actions, and critical alerts.
*   **Don't Use Sharp Corners:** While the theme is technical, use the `DEFAULT` (0.25rem) or `md` (0.375rem) roundedness to keep the UI feeling sophisticated and modern, rather than "retro-brutalist."