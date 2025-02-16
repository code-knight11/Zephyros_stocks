import React, { useState, useEffect } from 'react';

const StockSearch = ({ onStockSelect }) => {
  const [stocks, setStocks] = useState([]);
  const [query, setQuery] = useState("");
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mock data for development
  const mockStocks = [
    { stock_id: 1, symbol: "AAPL", company_name: "Apple Inc.", stock_type: "Common Stock" },
    { stock_id: 2, symbol: "MSFT", company_name: "Microsoft Corporation", stock_type: "Common Stock" },
    { stock_id: 3, symbol: "GOOGL", company_name: "Alphabet Inc.", stock_type: "Common Stock" },
    { stock_id: 4, symbol: "AMZN", company_name: "Amazon.com Inc.", stock_type: "Common Stock" },
    { stock_id: 5, symbol: "META", company_name: "Meta Platforms Inc.", stock_type: "Common Stock" },
    { stock_id: 6, symbol: "TSLA", company_name: "Tesla Inc.", stock_type: "Common Stock" },
    { stock_id: 7, symbol: "NVDA", company_name: "NVIDIA Corporation", stock_type: "Common Stock" },
    { stock_id: 8, symbol: "JPM", company_name: "JPMorgan Chase & Co.", stock_type: "Common Stock" },
    { stock_id: 9, symbol: "V", company_name: "Visa Inc.", stock_type: "Common Stock" },
    { stock_id: 10, symbol: "JNJ", company_name: "Johnson & Johnson", stock_type: "Common Stock" }
  ];

  // Fetch stocks on component mount
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        setIsLoading(true);
        // First try to fetch from API
        try {
            const response = await fetch("http://localhost:5002/api/getallstocks");
            if (!response.ok) {
            throw new Error("Failed to fetch stocks");
          }
          const data = await response.json();
          setStocks(data);
        } catch (apiError) {
          console.log("Using mock data due to API error:", apiError);
          // Fallback to mock data if API fails
          setStocks(mockStocks);
        }
        setError(null);
      } catch (err) {
        setError("Failed to load stocks. Using sample data.");
        setStocks(mockStocks); // Ensure we still have data to work with
      } finally {
        setIsLoading(false);
      }
    };

    fetchStocks();
  }, []);

  // Filter stocks based on search query
  useEffect(() => {
    if (!query.trim()) {
      setFilteredStocks([]);
      return;
    }

    const lowerQuery = query.toLowerCase().trim();
    const filtered = stocks.filter(stock => 
      stock.symbol.toLowerCase().includes(lowerQuery) ||
      stock.company_name.toLowerCase().includes(lowerQuery)
    ).slice(0, 10); // Limit to top 10 results

    setFilteredStocks(filtered);
  }, [query, stocks]);

  return (
    <div className="relative w-full">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search stocks by name or symbol..."
        className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
      
      {isLoading && (
        <div className="absolute w-full mt-1 p-2 bg-white rounded-lg shadow-lg border">
          Loading stocks...
        </div>
      )}

      {error && (
        <div className="absolute w-full mt-1 p-2 bg-red-50 text-red-500 rounded-lg shadow-lg border border-red-200">
          {error}
        </div>
      )}

      {filteredStocks.length > 0 && (
        <ul className="absolute z-10 w-full mt-1 bg-white rounded-lg shadow-lg border max-h-60 overflow-y-auto">
          {filteredStocks.map((stock) => (
            <li
              key={stock.stock_id}
              onClick={() => {
                onStockSelect(stock);
                setQuery('');
                setFilteredStocks([]);
              }}
              className="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
            >
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium">{stock.symbol}</span>
                  <span className="ml-2 text-gray-600">-</span>
                  <span className="ml-2 text-gray-600">{stock.company_name}</span>
                </div>
                <span className="text-sm text-gray-500">{stock.stock_type}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default StockSearch;
