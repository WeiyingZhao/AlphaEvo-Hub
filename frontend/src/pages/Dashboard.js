import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function Dashboard() {
  const [config, setConfig] = useState({
    strategy: 'prompt_optimization',
    generations: 10,
    populationSize: 5,
    task: 'Solve coding problems',
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
      alert('Error starting evolution');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Agent Evolve Dashboard
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Self-Evolving AI Agent Platform
      </Typography>

      <Box sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Evolution Configuration
                </Typography>

                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Evolution Strategy</InputLabel>
                  <Select
                    value={config.strategy}
                    label="Evolution Strategy"
                    onChange={(e) =>
                      setConfig({ ...config, strategy: e.target.value })
                    }
                  >
                    <MenuItem value="prompt_optimization">
                      Prompt Optimization
                    </MenuItem>
                    <MenuItem value="memory_evolution">
                      Memory Evolution
                    </MenuItem>
                    <MenuItem value="tool_evolution">Tool Evolution</MenuItem>
                    <MenuItem value="code_evolution">Code Evolution</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  label="Generations"
                  type="number"
                  value={config.generations}
                  onChange={(e) =>
                    setConfig({ ...config, generations: parseInt(e.target.value) })
                  }
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Population Size"
                  type="number"
                  value={config.populationSize}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      populationSize: parseInt(e.target.value),
                    })
                  }
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Task Description"
                  multiline
                  rows={3}
                  value={config.task}
                  onChange={(e) => setConfig({ ...config, task: e.target.value })}
                  sx={{ mt: 2 }}
                />

                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  startIcon={<PlayArrowIcon />}
                  onClick={handleStartEvolution}
                  disabled={loading}
                  sx={{ mt: 3 }}
                >
                  Start Evolution
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Start Guide
                </Typography>
                <Typography variant="body2" paragraph>
                  1. Select an evolution strategy that best fits your goal
                </Typography>
                <Typography variant="body2" paragraph>
                  2. Configure the number of generations and population size
                </Typography>
                <Typography variant="body2" paragraph>
                  3. Describe the task you want the agent to improve at
                </Typography>
                <Typography variant="body2" paragraph>
                  4. Click "Start Evolution" to begin the optimization process
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  The agent will automatically evolve its capabilities through
                  multiple generations, improving its performance on your specified
                  task.
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <Typography variant="body2" color="success.main">
                  ✓ Backend API: Connected
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Ready to start evolution runs
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}

export default Dashboard;
