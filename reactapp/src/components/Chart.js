import React, { useContext, useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { chartConfig } from "../constants/config";
import { mockHistoricalData } from "../constants/mock";
import { convertUnixTimestampToDate } from "../utils/helpers/date-helper";
import Card from "./Card";
import ChartFilter from "./ChartFilter";
import StockContext from "../context/StockContext";

const resolutionMap = {
  "1Y": "Y",
  "1M": "M",
  "1W": "W",
  "1D": "D",
};

const Chart = () => {
  const [data, setData] = useState();
  const [filter, setFilter] = useState("1W");
  const { stockSymbol } = useContext(StockContext);

  // useEffect(() => {
  //   (async () => {
  //     setData(await mockHistoricalData());
  //   })();
  // }, []);

  useEffect(() => {
    if (!stockSymbol) return;
    const fetchHistoricalData = async () => {
      try {
        const res = resolutionMap[filter] || "D"; // fallback to "D" if not found
        // Build the endpoint URL; the backend will compute the date range dynamically.
        const url = `http://127.0.0.1:5002/api/historical/${res}/${stockSymbol}`;
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error("Failed to fetch historical data");
        }
        const responseData = await response.json();
        setData(responseData);
      } catch (error) {
        console.error("Error fetching historical data:", error);
      }
    };

    fetchHistoricalData();
  }, [filter, stockSymbol]);

  // const formatData = (data) => {
  //   return data?.c.map((item, index) => {
  //     return {
  //       value: item.toFixed(2),
  //       date: convertUnixTimestampToDate(data.t[index]),
  //     };
  //   });
  // };

  const formatData = (data) => {
    if (!data || !data.c || !data.t) return [];
    return data.c.map((item, index) => ({
      value: Number(item.toFixed(2)),
      date: convertUnixTimestampToDate(data.t[index]),
    }));
  };

  return (
    <Card>
      <ul className="flex absolute top-2 right-2 z-40">
        {Object.keys(chartConfig).map((item) => (
          <li key={item}>
            <ChartFilter
              text={item}
              active={filter === item}
              onClick={() => {
                setFilter(item);
              }}
            />
          </li>
        ))}
      </ul>
      <ResponsiveContainer>
        <AreaChart data={formatData(data)}>
          <defs>
            <linearGradient id="chartColor" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor="rgb(199 210 254)"
                stopOpacity={0.8}
              />
              <stop offset="95%" stopColor="rgb(199 210 254)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="value"
            stroke="#312e81"
            fillOpacity={1}
            fill="url(#chartColor)"
            strokeWidth={0.5}
          />
          <Tooltip />
          <XAxis dataKey="date" />
          <YAxis domain={["dataMin", "dataMax"]} />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default Chart;
