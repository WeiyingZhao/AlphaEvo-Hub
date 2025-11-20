import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Grid,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function EvolutionView() {
  const { id } = useParams();
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Evolution Run: {id}
      </Typography>

      {status && (
        <Box sx={{ mt: 4 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Status
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {status.status}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={status.progress}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Generation
                  </Typography>
                  <Typography variant="h4" color="secondary">
                    {status.generation}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Best Score
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {status.best_score.toFixed(4)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {chartData.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Evolution Progress
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="generation" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#8884d8"
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {result && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Best Configuration
                </Typography>
                <Box
                  component="pre"
                  sx={{
                    p: 2,
                    bgcolor: 'grey.900',
                    borderRadius: 1,
                    overflow: 'auto',
                  }}
                >
                  {JSON.stringify(result.best_config, null, 2)}
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      )}
    </Container>
  );
}

export default EvolutionView;
