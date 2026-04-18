/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
    './src/app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
  	container: {
  		center: true,
  		padding: '2rem',
  		screens: {
  			'2xl': '1400px'
  		}
  	},
  	extend: {
  		colors: {
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			brand: {
  				primary: '#8b5cf6',
  				secondary: '#a855f7',
  				accent: '#c084fc',
  				dark: '#581c87',
  				light: '#e9d5ff',
  				background: '#0f0a1a',
  				surface: '#1a0f2e',
  				muted: '#9ca3af'
  			},
  			purple: {
  				'50': '#faf5ff',
  				'100': '#f3e8ff',
  				'200': '#e9d5ff',
  				'300': '#d8b4fe',
  				'400': '#c084fc',
  				'500': '#a855f7',
  				'600': '#9333ea',
  				'700': '#7c3aed',
  				'800': '#6b21a8',
  				'900': '#581c87',
  				'950': '#3b0764'
  			},
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: 0
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: 0
  				}
  			},
  			'fade-in': {
  				from: {
  					opacity: 0,
  					transform: 'translate3d(0, 10px, 0)'
  				},
  				to: {
  					opacity: 1,
  					transform: 'translate3d(0, 0, 0)'
  				}
  			},
  			'slide-in': {
  				from: {
  					transform: 'translate3d(-100%, 0, 0)'
  				},
  				to: {
  					transform: 'translate3d(0, 0, 0)'
  				}
  			},
  			'glow-purple': {
  				'0%, 100%': {
  					boxShadow: '0 0 20px rgba(139, 92, 246, 0.4)'
  				},
  				'50%': {
  					boxShadow: '0 0 30px rgba(168, 85, 247, 0.6)'
  				}
  			},
  			'pulse-purple': {
  				'0%, 100%': {
  					opacity: 1
  				},
  				'50%': {
  					opacity: 0.8
  				}
  			},
  			'float': {
  				'0%, 100%': {
  					transform: 'translate3d(0, 0px, 0)'
  				},
  				'50%': {
  					transform: 'translate3d(0, -10px, 0)'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out',
  			'fade-in': 'fade-in 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
  			'slide-in': 'slide-in 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  			'glow-purple': 'glow-purple 3s ease-in-out infinite',
  			'pulse-purple': 'pulse-purple 2s ease-in-out infinite',
  			'float': 'float 4s ease-in-out infinite'
  		},
  		backgroundImage: {
  			'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
  			'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
  			'purple-gradient': 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)',
  			'purple-dark-gradient': 'linear-gradient(135deg, #581c87 0%, #7c3aed 50%, #8b5cf6 100%)',
  			'purple-light-gradient': 'linear-gradient(135deg, #c084fc 0%, #e9d5ff 100%)',
  			'purple-radial': 'radial-gradient(circle at center, #8b5cf6 0%, #581c87 100%)'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
}