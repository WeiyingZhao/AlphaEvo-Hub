import { createTheme } from '@mui/material/styles';

// Neural Genesis Color Palette
const colors = {
  bgVoid: '#0a0a0f',
  bgSurface: '#12121a',
  bgCard: 'rgba(18, 18, 26, 0.8)',
  accentCyan: '#00f5d4',
  accentMagenta: '#f72585',
  accentGold: '#fca311',
  accentPurple: '#7209b7',
  textPrimary: '#e8e8e8',
  textMuted: '#6b7280',
  border: 'rgba(0, 245, 212, 0.1)',
};

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: colors.accentCyan,
      light: '#33f7dc',
      dark: '#00c4a9',
      contrastText: '#0a0a0f',
    },
    secondary: {
      main: colors.accentMagenta,
      light: '#f95097',
      dark: '#c51e6a',
    },
    warning: {
      main: colors.accentGold,
    },
    background: {
      default: colors.bgVoid,
      paper: colors.bgSurface,
    },
    text: {
      primary: colors.textPrimary,
      secondary: colors.textMuted,
    },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontFamily: '"Orbitron", "IBM Plex Sans", sans-serif',
      fontWeight: 700,
      letterSpacing: '0.05em',
    },
    h2: {
      fontFamily: '"Orbitron", "IBM Plex Sans", sans-serif',
      fontWeight: 600,
      letterSpacing: '0.04em',
    },
    h3: {
      fontFamily: '"Orbitron", "IBM Plex Sans", sans-serif',
      fontWeight: 600,
      letterSpacing: '0.03em',
    },
    h4: {
      fontFamily: '"Orbitron", "IBM Plex Sans", sans-serif',
      fontWeight: 500,
      letterSpacing: '0.02em',
    },
    h5: {
      fontFamily: '"IBM Plex Sans", sans-serif',
      fontWeight: 500,
    },
    h6: {
      fontFamily: '"IBM Plex Sans", sans-serif',
      fontWeight: 500,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
      fontSize: '0.75rem',
    },
    body1: {
      fontFamily: '"IBM Plex Sans", sans-serif',
      lineHeight: 1.7,
    },
    body2: {
      fontFamily: '"IBM Plex Sans", sans-serif',
      lineHeight: 1.6,
    },
    button: {
      fontFamily: '"Orbitron", "IBM Plex Sans", sans-serif',
      fontWeight: 600,
      letterSpacing: '0.05em',
    },
    code: {
      fontFamily: '"JetBrains Mono", "Fira Code", monospace',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: `linear-gradient(180deg, ${colors.bgVoid} 0%, #0d0d14 100%)`,
          minHeight: '100vh',
        },
        '::selection': {
          background: colors.accentCyan,
          color: colors.bgVoid,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: colors.bgCard,
          backdropFilter: 'blur(20px)',
          border: `1px solid ${colors.border}`,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            border: `1px solid rgba(0, 245, 212, 0.3)`,
            boxShadow: `0 8px 32px rgba(0, 245, 212, 0.1), 0 0 0 1px rgba(0, 245, 212, 0.1)`,
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '12px 24px',
          textTransform: 'uppercase',
          position: 'relative',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
        },
        contained: {
          background: `linear-gradient(135deg, ${colors.accentCyan} 0%, ${colors.accentPurple} 100%)`,
          boxShadow: `0 4px 20px rgba(0, 245, 212, 0.3)`,
          '&:hover': {
            background: `linear-gradient(135deg, ${colors.accentCyan} 0%, ${colors.accentMagenta} 100%)`,
            boxShadow: `0 6px 30px rgba(0, 245, 212, 0.5)`,
            transform: 'translateY(-2px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        outlined: {
          borderColor: colors.accentCyan,
          color: colors.accentCyan,
          '&:hover': {
            borderColor: colors.accentCyan,
            background: `rgba(0, 245, 212, 0.1)`,
            boxShadow: `0 0 20px rgba(0, 245, 212, 0.2)`,
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            background: 'rgba(10, 10, 15, 0.6)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease',
            '& fieldset': {
              borderColor: colors.border,
              transition: 'all 0.3s ease',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(0, 245, 212, 0.3)',
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.accentCyan,
              boxShadow: `0 0 0 2px rgba(0, 245, 212, 0.1)`,
            },
          },
          '& .MuiInputLabel-root': {
            color: colors.textMuted,
            fontFamily: '"IBM Plex Sans", sans-serif',
            '&.Mui-focused': {
              color: colors.accentCyan,
            },
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          background: 'rgba(10, 10, 15, 0.6)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          height: 8,
          borderRadius: 4,
          background: 'rgba(0, 245, 212, 0.1)',
        },
        bar: {
          borderRadius: 4,
          background: `linear-gradient(90deg, ${colors.accentCyan} 0%, ${colors.accentMagenta} 100%)`,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontFamily: '"IBM Plex Sans", sans-serif',
          fontWeight: 500,
        },
        filled: {
          background: 'rgba(0, 245, 212, 0.15)',
          color: colors.accentCyan,
          border: `1px solid rgba(0, 245, 212, 0.3)`,
        },
      },
    },
  },
});

export { colors };
export default theme;
