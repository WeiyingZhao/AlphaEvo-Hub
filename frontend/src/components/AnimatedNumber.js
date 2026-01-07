import React, { useEffect, useState, useRef } from 'react';
import { Typography } from '@mui/material';
import { motion, useSpring, useTransform } from 'framer-motion';

const AnimatedNumber = ({
  value,
  decimals = 0,
  duration = 1,
  prefix = '',
  suffix = '',
  color = 'primary',
  variant = 'h3',
  delay = 0,
  sx = {},
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  // Use spring animation for smooth counting
  const spring = useSpring(0, {
    stiffness: 50,
    damping: 20,
  });

  const display = useTransform(spring, (current) =>
    `${prefix}${current.toFixed(decimals)}${suffix}`
  );

  useEffect(() => {
    // Intersection observer for triggering animation when visible
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [isVisible]);

  useEffect(() => {
    if (isVisible) {
      const timeout = setTimeout(() => {
        spring.set(value);
      }, delay * 1000);
      return () => clearTimeout(timeout);
    }
  }, [isVisible, value, spring, delay]);

  // Update when value changes
  useEffect(() => {
    if (isVisible) {
      spring.set(value);
    }
  }, [value, isVisible, spring]);

  const colorMap = {
    primary: '#00f5d4',
    secondary: '#f72585',
    gold: '#fca311',
    white: '#e8e8e8',
  };

  return (
    <Typography
      ref={ref}
      component={motion.div}
      variant={variant}
      sx={{
        color: colorMap[color] || color,
        fontFamily: '"Orbitron", sans-serif',
        fontWeight: 700,
        textShadow: `0 0 20px ${colorMap[color] || color}40`,
        ...sx,
      }}
      {...props}
    >
      <motion.span>{display}</motion.span>
    </Typography>
  );
};

export default AnimatedNumber;
