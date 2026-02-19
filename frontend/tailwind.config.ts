import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './app/**/*.{js,ts,jsx,tsx}',
        './components/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {
            colors: {
                luxor: {
                    50: '#fdf8f0',
                    100: '#f9eddb',
                    200: '#f2d7b6',
                    300: '#e9ba87',
                    400: '#df9556',
                    500: '#d77a35',
                    600: '#c8622a',
                    700: '#a64b25',
                    800: '#853d25',
                    900: '#6c3321',
                    950: '#3a180f',
                },
                sand: {
                    50: '#faf8f5',
                    100: '#f0ece4',
                    200: '#e0d7c8',
                    300: '#ccbda5',
                    400: '#b69f82',
                    500: '#a6896a',
                    600: '#99785e',
                    700: '#80634f',
                    800: '#695144',
                    900: '#57443a',
                },
                night: {
                    50: '#f5f6f8',
                    100: '#e0e3e8',
                    200: '#c3c9d3',
                    300: '#9ea7b5',
                    400: '#7a8596',
                    500: '#606b7c',
                    600: '#4d5668',
                    700: '#414856',
                    800: '#383e4a',
                    900: '#1a1d24',
                    950: '#0d0f13',
                }
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
        },
    },
    plugins: [],
}
export default config
