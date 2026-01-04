/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    // In Tailwind v4, we must use this specific package
    '@tailwindcss/postcss': {}, 
  },
};

export default config;