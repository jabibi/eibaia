interface LabelColorClasses {
  /** Solid dot/swatch, e.g. the color picker grid and the closed ColorSelect indicator. */
  swatch: string;
  /** Tinted text, for subtle highlights (chips, row accents). */
  text: string;
  /** Light background tint, paired with `text` for chips and dropdown option rows. */
  chipBg: string;
}

// Single source of truth for the fixed color palette: add a color by adding one entry here —
// `LabelColor` and `LABEL_COLORS` are both derived from these keys, not listed separately.
export const LABEL_COLOR_CLASSES = {
  red: { swatch: "bg-red-500", text: "text-red-700", chipBg: "bg-red-50" },
  orange: { swatch: "bg-orange-500", text: "text-orange-700", chipBg: "bg-orange-50" },
  amber: { swatch: "bg-amber-500", text: "text-amber-700", chipBg: "bg-amber-50" },
  yellow: { swatch: "bg-yellow-500", text: "text-yellow-700", chipBg: "bg-yellow-50" },
  lime: { swatch: "bg-lime-500", text: "text-lime-700", chipBg: "bg-lime-50" },
  green: { swatch: "bg-green-500", text: "text-green-700", chipBg: "bg-green-50" },
  teal: { swatch: "bg-teal-500", text: "text-teal-700", chipBg: "bg-teal-50" },
  cyan: { swatch: "bg-cyan-500", text: "text-cyan-700", chipBg: "bg-cyan-50" },
  blue: { swatch: "bg-blue-500", text: "text-blue-700", chipBg: "bg-blue-50" },
  indigo: { swatch: "bg-indigo-500", text: "text-indigo-700", chipBg: "bg-indigo-50" },
  purple: { swatch: "bg-purple-500", text: "text-purple-700", chipBg: "bg-purple-50" },
  pink: { swatch: "bg-pink-500", text: "text-pink-700", chipBg: "bg-pink-50" },
  gray: { swatch: "bg-gray-500", text: "text-gray-700", chipBg: "bg-gray-100" },
  lightgray: { swatch: "bg-gray-300", text: "text-gray-600", chipBg: "bg-gray-50" },
} satisfies Record<string, LabelColorClasses>;

export type LabelColor = keyof typeof LABEL_COLOR_CLASSES;

export const LABEL_COLORS = Object.keys(LABEL_COLOR_CLASSES) as LabelColor[];

export const DEFAULT_LABEL_COLOR: LabelColor = "blue";
