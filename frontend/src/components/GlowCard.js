import React from 'react';
import { Box } from '@mui/material';
import { motion } from 'framer-motion';

const GlowCard = ({
  children,
  glowColor = 'cyan',
  delay = 0,
  hover = true,
  onClick,
  selected = false,
  sx = {},
  ...props
}) => {
  const glowColors = {
    cyan: {
      border: 'rgba(0, 245, 212, 0.2)',
      shadow: 'rgba(0, 245, 212, 0.15)',
      hoverBorder: 'rgba(0, 245, 212, 0.5)',
      hoverShadow: 'rgba(0, 245, 212, 0.3)',
    },
    magenta: {
      border: 'rgba(247, 37, 133, 0.2)',
      shadow: 'rgba(247, 37, 133, 0.15)',
      hoverBorder: 'rgba(247, 37, 133, 0.5)',
      hoverShadow: 'rgba(247, 37, 133, 0.3)',
    },
    gold: {
      border: 'rgba(252, 163, 17, 0.2)',
      shadow: 'rgba(252, 163, 17, 0.15)',
      hoverBorder: 'rgba(252, 163, 17, 0.5)',
      hoverShadow: 'rgba(252, 163, 17, 0.3)',
    },
  };

  const colors = glowColors[glowColor] || glowColors.cyan;

  return (
    <Box
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay,
        ease: [0.4, 0, 0.2, 1]
      }}
      whileHover={hover ? {
        y: -4,
        transition: { duration: 0.2 }
      } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      onClick={onClick}
      sx={{
        background: 'rgba(18, 18, 26, 0.8)',
        backdropFilter: 'blur(20px)',
        border: `1px solid ${selected ? colors.hoverBorder : colors.border}`,
        borderRadius: '16px',
        padding: 3,
        cursor: onClick ? 'pointer' : 'default',
        boxShadow: selected
          ? `0 8px 32px ${colors.hoverShadow}, 0 0 0 1px ${colors.hoverBorder}`
          : `0 8px 32px rgba(0, 0, 0, 0.4)`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': hover ? {
          borderColor: colors.hoverBorder,
          boxShadow: `0 12px 40px ${colors.hoverShadow}, 0 0 0 1px ${colors.hoverBorder}`,
        } : {},
        ...sx,
      }}
      {...props}
    >
      {children}
    </Box>
  );
};

export default GlowCard;
