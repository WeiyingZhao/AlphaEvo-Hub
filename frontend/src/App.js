import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Import fonts
import '@fontsource/orbitron/400.css';
import '@fontsource/orbitron/500.css';
import '@fontsource/orbitron/600.css';
import '@fontsource/orbitron/700.css';
import '@fontsource/ibm-plex-sans/300.css';
import '@fontsource/ibm-plex-sans/400.css';
import '@fontsource/ibm-plex-sans/500.css';
import '@fontsource/ibm-plex-sans/600.css';
import '@fontsource/jetbrains-mono/400.css';
import '@fontsource/jetbrains-mono/500.css';

// Import custom theme and styles
import theme from './styles/theme';
import './styles/global.css';

// Import components
import ParticleBackground from './components/ParticleBackground';
import Dashboard from './pages/Dashboard';
import EvolutionView from './pages/EvolutionView';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Animated particle background */}
        <ParticleBackground particleCount={60} speed={0.3} />

        {/* Grid overlay */}
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
              linear-gradient(rgba(0, 245, 212, 0.02) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 245, 212, 0.02) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />

        {/* Gradient orbs for ambient lighting */}
        <Box
          sx={{
            position: 'fixed',
            top: '-20%',
            left: '-10%',
            width: '50%',
            height: '50%',
            background: 'radial-gradient(circle, rgba(114, 9, 183, 0.15) 0%, transparent 60%)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />
        <Box
          sx={{
            position: 'fixed',
            bottom: '-20%',
            right: '-10%',
            width: '50%',
            height: '50%',
            background: 'radial-gradient(circle, rgba(0, 245, 212, 0.1) 0%, transparent 60%)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />

        {/* Main content */}
        <Router>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/evolution/:id" element={<EvolutionView />} />
          </Routes>
        </Router>
      </Box>
    </ThemeProvider>
  );
}

export default App;
