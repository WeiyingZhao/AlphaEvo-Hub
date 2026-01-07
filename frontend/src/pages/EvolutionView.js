import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Button,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import axios from 'axios';
import GlowCard from '../components/GlowCard';
import AnimatedNumber from '../components/AnimatedNumber';

const API_BASE_URL = 'http://localhost:8000';

// Animated Progress Ring Component
const ProgressRing = ({ progress, size = 120, strokeWidth = 8 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <Box sx={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(0, 245, 212, 0.1)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{
            filter: 'drop-shadow(0 0 8px rgba(0, 245, 212, 0.5))',
          }}
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00f5d4" />
            <stop offset="100%" stopColor="#7209b7" />
          </linearGradient>
        </defs>
      </svg>
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontFamily: '"Orbitron", sans-serif',
            fontWeight: 700,
            color: '#00f5d4',
            textShadow: '0 0 20px rgba(0, 245, 212, 0.5)',
          }}
        >
          {Math.round(progress)}%
        </Typography>
      </Box>
    </Box>
  );
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const statusConfig = {
    running: {
      color: '#00f5d4',
      bg: 'rgba(0, 245, 212, 0.15)',
      border: 'rgba(0, 245, 212, 0.3)',
      pulse: true,
    },
    completed: {
      color: '#fca311',
      bg: 'rgba(252, 163, 17, 0.15)',
      border: 'rgba(252, 163, 17, 0.3)',
      pulse: false,
    },
    failed: {
      color: '#f72585',
      bg: 'rgba(247, 37, 133, 0.15)',
      border: 'rgba(247, 37, 133, 0.3)',
      pulse: false,
    },
    pending: {
      color: '#6b7280',
      bg: 'rgba(107, 114, 128, 0.15)',
      border: 'rgba(107, 114, 128, 0.3)',
      pulse: false,
    },
  };

  const config = statusConfig[status] || statusConfig.pending;

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 1,
        px: 2,
        py: 0.75,
        background: config.bg,
        border: `1px solid ${config.border}`,
        borderRadius: '20px',
      }}
    >
      {config.pulse && (
        <Box
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: config.color,
            boxShadow: `0 0 10px ${config.color}`,
            animation: 'pulse 2s ease-in-out infinite',
          }}
        />
      )}
      <Typography
        sx={{
          color: config.color,
          fontFamily: '"IBM Plex Sans", sans-serif',
          fontWeight: 600,
          fontSize: '0.85rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}
      >
        {status}
      </Typography>
    </Box>
  );
};

// Custom Tooltip for Chart
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Box
        sx={{
          background: 'rgba(18, 18, 26, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0, 245, 212, 0.3)',
          borderRadius: '8px',
          p: 1.5,
        }}
      >
        <Typography
          variant="body2"
          sx={{ color: '#6b7280', fontSize: '0.75rem', mb: 0.5 }}
        >
          Generation {label}
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: '#00f5d4',
            fontFamily: '"Orbitron", sans-serif',
            fontWeight: 600,
          }}
        >
          Score: {payload[0].value.toFixed(4)}
        </Typography>
      </Box>
    );
  }
  return null;
};

function EvolutionView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/evolution/${id}/status`
        );
        setStatus(response.data);

        if (response.data.status === 'completed') {
          const resultResponse = await axios.get(
            `${API_BASE_URL}/evolution/${id}/result`
          );
          setResult(resultResponse.data);
        }
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);

    return () => clearInterval(interval);
  }, [id]);

  const chartData = result?.generation_scores?.map((score, index) => ({
    generation: index + 1,
    score: score,
  })) || [];

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
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 5,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                onClick={() => navigate('/')}
                startIcon={<ArrowBackIcon />}
                sx={{
                  color: 'text.secondary',
                  '&:hover': {
                    color: '#00f5d4',
                    background: 'rgba(0, 245, 212, 0.1)',
                  },
                }}
              >
                Back
              </Button>
              <Box>
                <Typography
                  variant="h4"
                  sx={{
                    fontFamily: '"Orbitron", sans-serif',
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #00f5d4 0%, #7209b7 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Evolution Run
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '0.8rem',
                    mt: 0.5,
                  }}
                >
                  ID: {id}
                </Typography>
              </Box>
            </Box>
            {status && <StatusBadge status={status.status} />}
          </Box>
        </motion.div>

        {status && (
          <>
            {/* Stats Cards */}
            <motion.div variants={itemVariants}>
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Progress Card */}
                <Grid item xs={12} md={4}>
                  <GlowCard glowColor="cyan" delay={0.1}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        py: 2,
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          mb: 2,
                        }}
                      >
                        <AutoAwesomeIcon sx={{ color: '#00f5d4', fontSize: 20 }} />
                        <Typography
                          variant="body2"
                          sx={{ color: 'text.secondary', fontWeight: 500 }}
                        >
                          Progress
                        </Typography>
                      </Box>
                      <ProgressRing progress={status.progress || 0} />
                    </Box>
                  </GlowCard>
                </Grid>

                {/* Generation Card */}
                <Grid item xs={12} md={4}>
                  <GlowCard glowColor="magenta" delay={0.2}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        py: 2,
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          mb: 2,
                        }}
                      >
                        <TrendingUpIcon sx={{ color: '#f72585', fontSize: 20 }} />
                        <Typography
                          variant="body2"
                          sx={{ color: 'text.secondary', fontWeight: 500 }}
                        >
                          Generation
                        </Typography>
                      </Box>
                      <AnimatedNumber
                        value={status.generation || 0}
                        color="secondary"
                        variant="h2"
                        delay={0.3}
                      />
                      <Typography
                        variant="body2"
                        sx={{
                          color: 'text.secondary',
                          mt: 1,
                          fontFamily: '"JetBrains Mono", monospace',
                        }}
                      >
                        / {status.total_generations || '?'}
                      </Typography>
                    </Box>
                  </GlowCard>
                </Grid>

                {/* Best Score Card */}
                <Grid item xs={12} md={4}>
                  <GlowCard glowColor="gold" delay={0.3}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        py: 2,
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          mb: 2,
                        }}
                      >
                        <EmojiEventsIcon sx={{ color: '#fca311', fontSize: 20 }} />
                        <Typography
                          variant="body2"
                          sx={{ color: 'text.secondary', fontWeight: 500 }}
                        >
                          Best Score
                        </Typography>
                      </Box>
                      <AnimatedNumber
                        value={status.best_score || 0}
                        decimals={4}
                        color="gold"
                        variant="h2"
                        delay={0.4}
                      />
                      <Chip
                        label="TOP"
                        size="small"
                        sx={{
                          mt: 1,
                          background: 'rgba(252, 163, 17, 0.15)',
                          color: '#fca311',
                          border: '1px solid rgba(252, 163, 17, 0.3)',
                          fontWeight: 600,
                          fontSize: '0.65rem',
                        }}
                      />
                    </Box>
                  </GlowCard>
                </Grid>
              </Grid>
            </motion.div>

            {/* Evolution Chart */}
            <AnimatePresence>
              {chartData.length > 0 && (
                <motion.div
                  variants={itemVariants}
                  initial="hidden"
                  animate="visible"
                  exit={{ opacity: 0, y: -20 }}
                >
                  <GlowCard delay={0.4} hover={false}>
                    <Typography
                      variant="h6"
                      sx={{
                        mb: 3,
                        color: 'text.secondary',
                        fontWeight: 500,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                      }}
                    >
                      <TrendingUpIcon sx={{ color: '#00f5d4' }} />
                      Evolution Progress
                    </Typography>

                    <Box sx={{ height: 350 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                          <defs>
                            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#00f5d4" stopOpacity={0.4} />
                              <stop offset="100%" stopColor="#00f5d4" stopOpacity={0} />
                            </linearGradient>
                            <filter id="glow">
                              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                              <feMerge>
                                <feMergeNode in="coloredBlur" />
                                <feMergeNode in="SourceGraphic" />
                              </feMerge>
                            </filter>
                          </defs>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="rgba(255, 255, 255, 0.05)"
                            vertical={false}
                          />
                          <XAxis
                            dataKey="generation"
                            stroke="#6b7280"
                            fontSize={12}
                            tickLine={false}
                            axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                          />
                          <YAxis
                            stroke="#6b7280"
                            fontSize={12}
                            tickLine={false}
                            axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                            tickFormatter={(value) => value.toFixed(2)}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Area
                            type="monotone"
                            dataKey="score"
                            stroke="#00f5d4"
                            strokeWidth={3}
                            fill="url(#scoreGradient)"
                            filter="url(#glow)"
                            dot={{
                              r: 4,
                              fill: '#00f5d4',
                              stroke: '#0a0a0f',
                              strokeWidth: 2,
                            }}
                            activeDot={{
                              r: 8,
                              fill: '#00f5d4',
                              stroke: 'rgba(0, 245, 212, 0.3)',
                              strokeWidth: 4,
                            }}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Box>
                  </GlowCard>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Best Configuration */}
            <AnimatePresence>
              {result && (
                <motion.div
                  variants={itemVariants}
                  initial="hidden"
                  animate="visible"
                  exit={{ opacity: 0, y: -20 }}
                >
                  <GlowCard delay={0.5} hover={false} sx={{ mt: 3 }}>
                    <Typography
                      variant="h6"
                      sx={{
                        mb: 3,
                        color: 'text.secondary',
                        fontWeight: 500,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                      }}
                    >
                      <EmojiEventsIcon sx={{ color: '#fca311' }} />
                      Best Configuration
                    </Typography>

                    <Box
                      component={motion.pre}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.2 }}
                      sx={{
                        p: 3,
                        background: 'rgba(0, 0, 0, 0.4)',
                        borderRadius: '12px',
                        border: '1px solid rgba(0, 245, 212, 0.1)',
                        overflow: 'auto',
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '0.85rem',
                        lineHeight: 1.8,
                        color: '#e8e8e8',
                        position: 'relative',
                        '&::before': {
                          content: '"JSON"',
                          position: 'absolute',
                          top: 12,
                          right: 12,
                          fontSize: '0.65rem',
                          color: '#6b7280',
                          background: 'rgba(255, 255, 255, 0.05)',
                          px: 1,
                          py: 0.25,
                          borderRadius: '4px',
                          letterSpacing: '0.05em',
                        },
                        '& .key': {
                          color: '#f72585',
                        },
                        '& .string': {
                          color: '#00f5d4',
                        },
                        '& .number': {
                          color: '#fca311',
                        },
                      }}
                    >
                      {JSON.stringify(result.best_config, null, 2)
                        .replace(/"([^"]+)":/g, '<span class="key">"$1"</span>:')
                        .replace(/: "([^"]+)"/g, ': <span class="string">"$1"</span>')
                        .replace(/: (\d+\.?\d*)/g, ': <span class="number">$1</span>')
                        .split('\n')
                        .map((line, i) => (
                          <span
                            key={i}
                            dangerouslySetInnerHTML={{ __html: line + '\n' }}
                          />
                        ))}
                    </Box>
                  </GlowCard>
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}

        {/* Loading State */}
        {!status && (
          <motion.div variants={itemVariants}>
            <GlowCard delay={0.1}>
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  py: 6,
                }}
              >
                <Box className="dna-helix" sx={{ mb: 3 }}>
                  {[...Array(5)].map((_, i) => (
                    <Box key={i} className="strand">
                      <Box className="dot" />
                      <Box className="dot" />
                    </Box>
                  ))}
                </Box>
                <Typography
                  variant="body1"
                  sx={{ color: 'text.secondary', fontWeight: 500 }}
                >
                  Loading evolution data...
                </Typography>
              </Box>
            </GlowCard>
          </motion.div>
        )}
      </motion.div>
    </Container>
  );
}

export default EvolutionView;
