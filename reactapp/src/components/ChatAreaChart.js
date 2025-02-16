import React, { useEffect, useRef, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ChatAreaChart = ({ symbols = [] }) => {
  const containerRef = useRef(null);
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch data for each symbol
        const dataPromises = symbols.map(symbol => 
          fetch(`http://127.0.0.1:5002/api/historical/D/${symbol}`)
            .then(res => {
              if (!res.ok) throw new Error(`Failed to fetch data for ${symbol}`);
              return res.json();
            })
        );

        const results = await Promise.all(dataPromises);
        
        // Process and combine the data
        const processedData = {};
        results.forEach((result, index) => {
          const symbol = symbols[index];
          // Assuming the API returns t (timestamps) and c (closing prices)
          result.t.forEach((timestamp, i) => {
            const date = new Date(timestamp * 1000).toLocaleDateString();
            if (!processedData[date]) {
              processedData[date] = { date };
            }
            processedData[date][symbol] = result.c[i];
          });
        });

        // Convert to array format for Recharts and sort by date
        const chartDataArray = Object.values(processedData).sort((a, b) => 
          new Date(a.date) - new Date(b.date)
        );

        setChartData(chartDataArray);
      } catch (err) {
        console.error('Error fetching stock data:', err);
        setError('Failed to load stock data');
      } finally {
        setIsLoading(false);
      }
    };

    if (symbols.length > 0) {
      fetchStockData();
    }
  }, [symbols]);

  if (isLoading) {
    return (
      <div className="w-full min-w-[500px] h-[300px] bg-white rounded-lg p-4 flex items-center justify-center">
        Loading chart data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full min-w-[500px] h-[300px] bg-white rounded-lg p-4 flex items-center justify-center text-red-500">
        {error}
      </div>
    );
  }

  // Sort symbols based on the latest closing price (lowest first)
  const sortedSymbols = chartData.length > 0 
    ? [...symbols].sort((a, b) => {
        const aVal = chartData[chartData.length - 1][a] || 0;
        const bVal = chartData[chartData.length - 1][b] || 0;
        return aVal - bVal;
      })
    : symbols;

  return (
    <div ref={containerRef} className="w-full min-w-[500px] h-[300px] bg-white rounded-lg p-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          {sortedSymbols.map((symbol, index) => (
            <Area
              key={symbol}
              type="monotone"
              dataKey={symbol}
              stackId="1"
              stroke={`hsl(${(index * 137.5) % 360}, 70%, 50%)`}
              fill={`hsl(${(index * 137.5) % 360}, 70%, 70%)`}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChatAreaChart;
