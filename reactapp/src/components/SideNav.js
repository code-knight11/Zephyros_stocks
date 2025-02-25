import React, { useContext, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import ThemeContext from "../context/ThemeContext";
import StockSearch from "../components/StockSearch";
import AreaChartExample from "./ChatAreaChart"; // import the chart component

const SideNav = ({ addBotMessage, onConversationSelect, currentThreadId }) => {
  const { darkMode } = useContext(ThemeContext);
  const [conversations, setConversations] = useState([]);
  const [showGraphOverlay, setShowGraphOverlay] = useState(false);
  const [selectedStocks, setSelectedStocks] = useState([]); // Store selected stocks
  const userId = localStorage.getItem("user_id");
  const navigate = useNavigate();

  // Fetch conversations for this user.
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/api/conversations/${userId}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch conversations");
        }
        const data = await response.json();
        setConversations(data.conversations);
      } catch (error) {
        console.error("Error fetching conversations:", error);
      }
    };

    if (userId) {
      fetchConversations();
    }
  }, [userId]);

  // Start a new conversation by calling the backend endpoint.
  const handleStartNewConversation = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/new_conversation/${userId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );
      if (!response.ok) {
        throw new Error("Failed to start a new conversation");
      }
      const data = await response.json();
      // Pass the new thread_id to the conversation selection callback.
      onConversationSelect(data.thread_id);
    } catch (error) {
      console.error("Error starting new conversation:", error);
      addBotMessage("Error: Could not start a new conversation.");
    }
  };

  // Existing graph generation functionality.
  const handleGenerateGraph = () => {
    setShowGraphOverlay(true);
  };

  const handleCloseOverlay = () => {
    setShowGraphOverlay(false);
    setSelectedStocks([]); // Clear selected stocks when closing overlay
  };

  const handleStockSelect = (stock) => {
    if (!selectedStocks.some((s) => s.stock_id === stock.stock_id)) {
      setSelectedStocks([...selectedStocks, stock]); // Add stock if not already selected
    }
  };

  const handleRemoveStock = (stockId) => {
    setSelectedStocks(selectedStocks.filter((s) => s.stock_id !== stockId)); // Remove stock
  };

  const handleGenerateCharts = () => {
    const symbols = selectedStocks.map((stock) => stock.symbol);
    // Pass the AreaChartExample as a message via addBotMessage.
    addBotMessage(<AreaChartExample symbols={symbols} />);
    handleCloseOverlay();
  };

  const handleLogout = () => {
    localStorage.removeItem("user_id");
  };

  return (
    <>
      {/* Sidebar Navigation */}
      <aside
        className={`fixed top-0 left-0 h-screen flex flex-col justify-between w-64 py-6 px-2 shadow-md ${
          darkMode
            ? "bg-gray-900 text-gray-300"
            : "bg-neutral-100 text-gray-800"
        }`}
      >
        <div>
          {/* Brand / Logo */}
          <Link
            className="text-2xl font-bold font-mono underline flex gap-2"
            to="/dashboard"
          >
            <img src="logo.png" className="w-8 h-8" />
            <p>Stockbot</p>
          </Link>

          <div className="border-t-2 my-4 rounded-md border-indigo-500" />

          <nav>
            <ul className="space-y-4">
              <li
                className="cursor-pointer hover:bg-indigo-500 py-1 px-1 rounded-md"
                onClick={() => navigate("/dashboard")}
              >
                Home
              </li>
              <li
                className="cursor-pointer hover:bg-indigo-500 py-1 px-1 rounded-md"
                onClick={() => navigate("/chat")}
              >
                Chatbot
              </li>
              <li
                className="cursor-pointer hover:bg-indigo-500 py-1 px-1 rounded-md"
                onClick={() => navigate("/portfolio")}
              >
                Portfolio
              </li>
              <li
                className="cursor-pointer hover:bg-indigo-500 py-1 px-1 rounded-md"
                onClick={() => {
                  handleLogout();
                  navigate("/");
                }}
              >
                Logout
              </li>
            </ul>
            {/* Indigo line after the navigation list */}
            <hr className="mt-4 border-t-2 border-indigo-500" />

            {/* Conversations Section */}
            <div className="mt-4 flex flex-col space-y-2">
              {/* Fixed height conversation list (50px) with custom scrollbar */}
              <div
                className={`overflow-y-auto custom-scrollbar ${
                  darkMode ? "custom-scrollbar-dark" : ""
                }`}
                style={{ height: "200px" }}
              >
                {conversations.length > 0 ? (
                  conversations.map((conv) => (
                    <button
                      key={conv.thread_id}
                      onClick={() => onConversationSelect(conv.thread_id)}
                      className={`block w-full text-left px-2 py-1 hover:bg-indigo-500 hover:text-white transition-colors ${
                        currentThreadId === conv.thread_id
                          ? "bg-indigo-500 text-white"
                          : ""
                      }`}
                    >
                      {conv.conversation_name}
                    </button>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">No conversations yet.</p>
                )}
              </div>

              {/* New Buttons below the conversation list */}
            </div>
          </nav>
        </div>

        <div>
          <button
            onClick={handleStartNewConversation}
            className="mt-2 w-full px-4 py-2 bg-indigo-400 text-white rounded hover:bg-indigo-500 transition-colors"
          >
            Start New Conversation
          </button>
          <button
            onClick={handleGenerateGraph}
            className="mt-2 w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
          >
            Generate a Graph
          </button>
        </div>
      </aside>

      {/* Graph Selection Overlay */}
      {showGraphOverlay && (
        <div className="fixed inset-bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96 relative">
            {/* Close Button */}
            <button
              onClick={handleCloseOverlay}
              className="absolute top-2 right-2 text-gray-600 hover:text-gray-900"
            >
              ✖
            </button>

            <h2 className="text-xl font-semibold mb-4">
              Select Stocks for Graph
            </h2>

            {/* Display Selected Stocks as Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {selectedStocks.map((stock) => (
                <div
                  key={stock.stock_id}
                  className="flex items-center bg-indigo-500 text-white px-3 py-1 rounded-full text-sm"
                >
                  {stock.symbol}
                  <button
                    onClick={() => handleRemoveStock(stock.stock_id)}
                    className="ml-2 text-white hover:text-gray-300"
                  >
                    ✖
                  </button>
                </div>
              ))}
            </div>

            {/* Stock Search Component */}
            <StockSearch onStockSelect={handleStockSelect} />

            {/* Generate Charts Button */}
            <button
              onClick={handleGenerateCharts}
              disabled={selectedStocks.length === 0}
              className={`mt-4 w-full px-4 py-2 rounded ${
                selectedStocks.length > 0
                  ? "bg-green-600 text-white hover:bg-green-700 transition-colors"
                  : "bg-gray-300 text-gray-600 cursor-not-allowed"
              }`}
            >
              Generate Charts
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default SideNav;
