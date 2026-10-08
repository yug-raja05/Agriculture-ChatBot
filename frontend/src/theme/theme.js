import { createTheme } from '@mui/material/styles';

/**
 * Custom Material-UI Palette designed to match Tailwind's custom green agriculture system
 */
export const getMuiTheme = (mode) => {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: '#1b5e20',      // Deep Forest Green
        light: '#2e7d32',
        dark: '#0d3c12',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#8d6e63',      // Clay Earthy Brown
        light: '#d7ccc8',
        dark: '#4e342e',
      },
      background: {
        default: mode === 'dark' ? '#0b130e' : '#f8f9fa',
        paper: mode === 'dark' ? '#121e16' : '#ffffff',
      },
      text: {
        primary: mode === 'dark' ? '#f1f5f9' : '#0f172a',
        secondary: mode === 'dark' ? '#94a3b8' : '#475569',
      },
      divider: mode === 'dark' ? 'rgba(31, 51, 38, 0.45)' : 'rgba(0, 0, 0, 0.08)',
    },
    typography: {
      fontFamily: '"Outfit", "Inter", "Helvetica", "Arial", sans-serif',
      h1: { fontWeight: 700 },
      h2: { fontWeight: 700 },
      h3: { fontWeight: 600 },
      h4: { fontWeight: 600 },
      h5: { fontWeight: 500 },
      h6: { fontWeight: 500 },
      button: { textTransform: 'none', fontWeight: 600 },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: '12px',
            padding: '8px 20px',
            boxShadow: 'none',
            '&:hover': {
              boxShadow: 'none',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: '16px',
            border: mode === 'dark' ? '1px solid rgba(31, 51, 38, 0.45)' : '1px solid rgba(0, 0, 0, 0.06)',
            boxShadow: 'none',
          },
        },
      },
    },
  });
};
