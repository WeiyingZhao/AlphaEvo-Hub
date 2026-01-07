import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Grid,
  Slider,
  Chip,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import PsychologyIcon from '@mui/icons-material/Psychology';
import MemoryIcon from '@mui/icons-material/Memory';
import BuildIcon from '@mui/icons-material/Build';
import CodeIcon from '@mui/icons-material/Code';
import axios from 'axios';
import GlowCard from '../components/GlowCard';

const API_BASE_URL = 'http://localhost:8000';

const strategies = [
  {
    id: 'prompt_optimization',
    name: 'Prompt Optimization',
    icon: PsychologyIcon,
    description: 'Evolve system prompts for better reasoning',
    color: 'cyan',
  },
  {
    id: 'memory_evolution',
    name: 'Memory Evolution',
    icon: MemoryIcon,
    description: 'Optimize memory retention and retrieval',
    color: 'magenta',
  },
  {
    id: 'tool_evolution',
    name: 'Tool Evolution',
    icon: BuildIcon,
    description: 'Adapt and refine tool usage patterns',
    color: 'cyan',
  },
  {
    id: 'code_evolution',
    name: 'Code Evolution',
    icon: CodeIcon,
    description: 'Generate and optimize code solutions',
    color: 'magenta',
  },
];

function Dashboard() {
  const [config, setConfig] = useState({
    strategy: 'prompt_optimization',
    generations: 10,
    populationSize: 5,
    task: '',
  });
  const [loading, setLoading] = useState(false);

  const handleStartEvolution = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/evolution/start`, {
        agent_config: {
          model_name: 'gpt-3.5-turbo',
          task: config.task,
        },
        strategy: config.strategy,
        generations: config.generations,
        population_size: config.populationSize,
      });
      console.log('Evolution started:', response.data);
      alert(`Evolution started! ID: ${response.data.evolution_id}`);
    } catch (error) {
      console.error('Error starting evolution:', error);
      alert('Error starting evolution. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: [0.4, 0, 0.2, 1],
      },
    },
  };

  return (
    <Container maxWidth="lg" sx={{ py: 6, position: 'relative', zIndex: 1 }}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Hero Section */}
        <motion.div variants={itemVariants}>
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                mb: 2,
                px: 2,
                py: 0.5,
                background: 'rgba(0, 245, 212, 0.1)',
                borderRadius: '20px',
                border: '1px solid rgba(0, 245, 212, 0.2)',
              }}
            >
              <AutoAwesomeIcon sx={{ fontSize: 16, color: '#00f5d4' }} />
              <Typography
                variant="body2"
                sx={{
                  color: '#00f5d4',
                  fontFamily: '"IBM Plex Sans", sans-serif',
                  fontWeight: 500,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  fontSize: '0.75rem',
                }}
              >
                Self-Evolving AI Platform
              </Typography>
            </Box>

            <Typography
              variant="h2"
              sx={{
                fontFamily: '"Orbitron", sans-serif',
                fontWeight: 700,
                fontSize: { xs: '2rem', md: '3.5rem' },
                background: 'linear-gradient(135deg, #00f5d4 0%, #7209b7 50%, #f72585 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
              }}
            >
              EVOLVE YOUR AI
            </Typography>

            <Typography
              variant="body1"
              sx={{
                color: 'text.secondary',
                maxWidth: 500,
                mx: 'auto',
                lineHeight: 1.8,
              }}
            >
              Configure and launch evolutionary optimization to create
              intelligent agents that continuously improve.
            </Typography>
          </Box>
        </motion.div>

        {/* Strategy Selection */}
        <motion.div variants={itemVariants}>
          <Typography
            variant="h6"
            sx={{
              mb: 3,
              color: 'text.secondary',
              fontWeight: 500,
            }}
          >
            Select Evolution Strategy
          </Typography>

          <Grid container spacing={2} sx={{ mb: 5 }}>
            {strategies.map((strategy, index) => {
              const Icon = strategy.icon;
              const isSelected = config.strategy === strategy.id;

              return (
                <Grid item xs={12} sm={6} md={3} key={strategy.id}>
                  <GlowCard
                    glowColor={strategy.color}
                    delay={0.1 * index}
                    onClick={() => setConfig({ ...config, strategy: strategy.id })}
                    selected={isSelected}
                    sx={{
                      height: '100%',
                      p: 2.5,
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: '12px',
                        background: isSelected
                          ? strategy.color === 'cyan'
                            ? 'linear-gradient(135deg, rgba(0, 245, 212, 0.3) 0%, rgba(114, 9, 183, 0.3) 100%)'
                            : 'linear-gradient(135deg, rgba(247, 37, 133, 0.3) 0%, rgba(114, 9, 183, 0.3) 100%)'
                          : 'rgba(255, 255, 255, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                        transition: 'all 0.3s ease',
                      }}
                    >
                      <Icon
                        sx={{
                          fontSize: 24,
                          color: isSelected
                            ? strategy.color === 'cyan' ? '#00f5d4' : '#f72585'
                            : 'text.secondary',
                          transition: 'all 0.3s ease',
                        }}
                      />
                    </Box>

                    <Typography
                      variant="subtitle1"
                      sx={{
                        fontWeight: 600,
                        mb: 0.5,
                        color: isSelected ? 'text.primary' : 'text.secondary',
                        transition: 'all 0.3s ease',
                      }}
                    >
                      {strategy.name}
                    </Typography>

                    <Typography
                      variant="body2"
                      sx={{
                        color: 'text.secondary',
                        fontSize: '0.8rem',
                        lineHeight: 1.5,
                      }}
                    >
                      {strategy.description}
                    </Typography>

                    {isSelected && (
                      <Chip
                        label="Selected"
                        size="small"
                        sx={{
                          mt: 2,
                          background: 'rgba(0, 245, 212, 0.15)',
                          color: '#00f5d4',
                          border: '1px solid rgba(0, 245, 212, 0.3)',
                          fontWeight: 500,
                          fontSize: '0.7rem',
                        }}
                      />
                    )}
                  </GlowCard>
                </Grid>
              );
            })}
          </Grid>
        </motion.div>

        {/* Configuration Panel */}
        <motion.div variants={itemVariants}>
          <GlowCard delay={0.4} hover={false}>
            <Typography
              variant="h6"
              sx={{
                mb: 4,
                color: 'text.secondary',
                fontWeight: 500,
              }}
            >
              Evolution Parameters
            </Typography>

            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Generations
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#00f5d4',
                        fontFamily: '"Orbitron", sans-serif',
                        fontWeight: 600,
                      }}
                    >
                      {config.generations}
                    </Typography>
                  </Box>
                  <Slider
                    value={config.generations}
                    onChange={(_, value) => setConfig({ ...config, generations: value })}
                    min={1}
                    max={50}
                    sx={{
                      '& .MuiSlider-track': {
                        background: 'linear-gradient(90deg, #00f5d4 0%, #7209b7 100%)',
                        border: 'none',
                      },
                      '& .MuiSlider-thumb': {
                        background: '#00f5d4',
                        boxShadow: '0 0 10px rgba(0, 245, 212, 0.5)',
                        '&:hover': {
                          boxShadow: '0 0 20px rgba(0, 245, 212, 0.7)',
                        },
                      },
                      '& .MuiSlider-rail': {
                        background: 'rgba(0, 245, 212, 0.1)',
                      },
                    }}
                  />
                </Box>

                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Population Size
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#f72585',
                        fontFamily: '"Orbitron", sans-serif',
                        fontWeight: 600,
                      }}
                    >
                      {config.populationSize}
                    </Typography>
                  </Box>
                  <Slider
                    value={config.populationSize}
                    onChange={(_, value) => setConfig({ ...config, populationSize: value })}
                    min={1}
                    max={20}
                    sx={{
                      '& .MuiSlider-track': {
                        background: 'linear-gradient(90deg, #f72585 0%, #7209b7 100%)',
                        border: 'none',
                      },
                      '& .MuiSlider-thumb': {
                        background: '#f72585',
                        boxShadow: '0 0 10px rgba(247, 37, 133, 0.5)',
                        '&:hover': {
                          boxShadow: '0 0 20px rgba(247, 37, 133, 0.7)',
                        },
                      },
                      '& .MuiSlider-rail': {
                        background: 'rgba(247, 37, 133, 0.1)',
                      },
                    }}
                  />
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Task Description"
                  placeholder="Describe the task you want your AI agent to excel at..."
                  multiline
                  rows={4}
                  value={config.task}
                  onChange={(e) => setConfig({ ...config, task: e.target.value })}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontFamily: '"IBM Plex Sans", sans-serif',
                    },
                  }}
                />
              </Grid>
            </Grid>

            {/* Start Button */}
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Button
                component={motion.button}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                variant="contained"
                size="large"
                startIcon={
                  loading ? (
                    <Box className="dna-helix" sx={{ transform: 'scale(0.5)', mr: 1 }}>
                      {[...Array(3)].map((_, i) => (
                        <Box key={i} className="strand" sx={{ gap: '10px' }}>
                          <Box className="dot" sx={{ width: 4, height: 4 }} />
                          <Box className="dot" sx={{ width: 4, height: 4 }} />
                        </Box>
                      ))}
                    </Box>
                  ) : (
                    <PlayArrowIcon />
                  )
                }
                onClick={handleStartEvolution}
                disabled={loading || !config.task.trim()}
                sx={{
                  px: 6,
                  py: 1.5,
                  fontSize: '1rem',
                  background: loading
                    ? 'rgba(0, 245, 212, 0.2)'
                    : 'linear-gradient(135deg, #00f5d4 0%, #7209b7 100%)',
                  '&:disabled': {
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'rgba(255, 255, 255, 0.3)',
                  },
                }}
              >
                {loading ? 'Initializing...' : 'Start Evolution'}
              </Button>

              <Typography
                variant="body2"
                sx={{
                  mt: 2,
                  color: 'text.secondary',
                  fontSize: '0.8rem',
                }}
              >
                The agent will evolve through {config.generations} generations
                with a population of {config.populationSize}
              </Typography>
            </Box>
          </GlowCard>
        </motion.div>

        {/* Status Indicator */}
        <motion.div variants={itemVariants}>
          <Box
            sx={{
              mt: 4,
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: '#00f5d4',
                boxShadow: '0 0 10px rgba(0, 245, 212, 0.5)',
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            <Typography
              variant="body2"
              sx={{
                color: 'text.secondary',
                fontSize: '0.8rem',
              }}
            >
              Backend API Connected
            </Typography>
          </Box>
        </motion.div>
      </motion.div>
    </Container>
  );
}

export default Dashboard;
