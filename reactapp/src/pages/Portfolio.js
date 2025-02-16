

import React, { useContext, useEffect, useState } from "react";
import ThemeContext from "../context/ThemeContext";
import TopNav from "../components/TopNav";
import StockSearch from "../components/StockSearch";

const Portfolio = () => {
  const { darkMode } = useContext(ThemeContext);
  const [portfolio, setPortfolio] = useState([]);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [newPortfolio, setNewPortfolio] = useState({
    symbol: "",
    company_name: "",
    stock_id: "",
    share_quantity: "",
    purchase_price: "",
    purchase_date: "" // new field for the purchase date
  });

  // Fetch the user's portfolio from the backend.
  useEffect(() => {
    const fetchPortfolio = async () => {
      const userId = localStorage.getItem("user_id");
      if (!userId) {
        console.error("User ID not found in local storage.");
        return;
      }
      try {
        const response = await fetch(`http://127.0.0.1:5002/api/profile/${userId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch portfolio");
        }
        const data = await response.json();
        console.log(data.portfolio);
        setPortfolio(data.portfolio);
      } catch (error) {
        console.error("Error fetching portfolio:", error);
      }
    };

    fetchPortfolio();
  }, []);

  // When a user selects a stock from the search results,
  // update the newPortfolio state with the stock's details.
  const handleStockSelect = (stock) => {
    setNewPortfolio((prev) => ({
      ...prev,
      symbol: stock.symbol,
      company_name: stock.company_name,
      stock_id: stock.stock_id
    }));
  };

  // When the form is submitted, send the portfolio data (including purchase_date) to the backend.
  const handleSubmit = async (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    const portfolioData = {
      ...newPortfolio,
      share_quantity: Number(newPortfolio.share_quantity),
      purchase_price: Number(newPortfolio.purchase_price),
      user_id: userId,
      purchase_date: newPortfolio.purchase_date
    };
    try {
      const response = await fetch("http://127.0.0.1:5002/api/addportfolio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(portfolioData)
      });
      if (!response.ok) {
        throw new Error("Failed to save portfolio");
      }
      const savedPortfolio = await response.json();
      setPortfolio((prev) => [...prev, savedPortfolio]);
      setIsOverlayOpen(false);
      setNewPortfolio({
        symbol: "",
        company_name: "",
        stock_id: "",
        share_quantity: "",
        purchase_price: "",
        purchase_date: ""
      });
    } catch (error) {
      console.error("Error saving portfolio:", error);
    }
  };

  return (
    <div
      className={`h-screen gap-10 px-5 font-quicksand ${
        darkMode ? "bg-gray-900 text-gray-300" : "bg-neutral-100"
      }`}
    >
      <TopNav />
      <div className="flex justify-between items-center mb-6 mt-28">
        <h1 className="text-3xl font-bold">Your Portfolio</h1>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          onClick={() => setIsOverlayOpen(true)}
        >
          Add Portfolio
        </button>
      </div>

      <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className={darkMode ? "bg-gray-700" : "bg-gray-50"}>
                <th className="px-6 py-4 text-left font-semibold">Symbol</th>
                <th className="px-6 py-4 text-left font-semibold">Company Name</th>
                <th className="px-6 py-4 text-right font-semibold">Share Quantity</th>
                <th className="px-6 py-4 text-right font-semibold">Purchase Price</th>
                <th className="px-6 py-4 text-right font-semibold">Purchase Date</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.map((stock, index) => (
                <tr
                  key={stock.portfolio_id || `${stock.symbol}-${index}`}
                  className="border-t border-gray-200 dark:border-gray-700"
                >
                  <td className="px-6 py-4">{stock.symbol}</td>
                  <td className="px-6 py-4">{stock.company_name}</td>
                  <td className="px-6 py-4 text-right">{stock.share_quantity}</td>
                  <td className="px-6 py-4 text-right">
                    ${stock.purchase_price.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">{stock.purchase_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {isOverlayOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg w-auto">
            <h2 className="text-xl font-bold mb-4">Add Portfolio Item</h2>
            <StockSearch onStockSelect={handleStockSelect} />
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                name="company_name"
                placeholder="Company Name"
                value={newPortfolio.company_name}
                className="w-full mb-2 p-2 border rounded"
                readOnly
              />
              <input
                type="text"
                name="symbol"
                placeholder="Symbol"
                value={newPortfolio.symbol}
                className="w-full mb-2 p-2 border rounded bg-gray-200"
                readOnly
              />
              {/* Include stock_id as a hidden field */}
              <input type="hidden" name="stock_id" value={newPortfolio.stock_id} />
              <input
                type="number"
                name="share_quantity"
                placeholder="Share Quantity"
                value={newPortfolio.share_quantity}
                onChange={(e) =>
                  setNewPortfolio({ ...newPortfolio, share_quantity: e.target.value })
                }
                className="w-full mb-2 p-2 border rounded"
                required
              />
              <input
                type="number"
                name="purchase_price"
                placeholder="Purchase Price"
                value={newPortfolio.purchase_price}
                onChange={(e) =>
                  setNewPortfolio({ ...newPortfolio, purchase_price: e.target.value })
                }
                className="w-full mb-2 p-2 border rounded"
                required
              />
              {/* Datepicker for purchase_date */}
              <input
                type="date"
                name="purchase_date"
                placeholder="Purchase Date"
                value={newPortfolio.purchase_date}
                onChange={(e) =>
                  setNewPortfolio({ ...newPortfolio, purchase_date: e.target.value })
                }
                className="w-full mb-2 p-2 border rounded"
                required
              />
              <div className="flex justify-end mt-4">
                <button
                  type="button"
                  className="mr-2 px-4 py-2 bg-gray-400 text-white rounded-lg"
                  onClick={() => setIsOverlayOpen(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg">
                  Submit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Portfolio;
