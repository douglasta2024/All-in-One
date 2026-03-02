/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas:  '#111318',   // base layer — blue-shifted dark, not neutral gray
        surface: '#181b22',   // raised surface (bubbles, sidebar active)
        raised:  '#1f2332',   // further elevated (hover states)
        pit:     '#0c0f14',   // recessed — inputs receive content, they're inset
        signal:  '#bf6a60',   // accent: YouTube red at half saturation
        done:    '#5b9e7c',   // sage green — quiet, not neon
        fault:   '#c46060',   // muted red
        ink: {
          1: '#e4e6ed',       // primary
          2: '#8b92a5',       // secondary
          3: '#545c70',       // tertiary
          4: '#2a2f3d',       // muted / placeholder
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['ui-monospace', 'JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
