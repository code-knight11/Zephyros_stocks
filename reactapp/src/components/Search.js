import React, { useContext, useState } from "react";
import ThemeContext from "../context/ThemeContext";
import StockContext from "../context/StockContext";
import { mockSearchResults } from "../constants/mock";
import SearchResults from "./SearchResults";
import { SearchIcon, XIcon } from "@heroicons/react/solid";
import axios from "axios";

const API_BASE = "http://localhost:5002/api"

const Search = () => {
  const { darkMode } = useContext(ThemeContext);
  const { setStockSymbol } = useContext(StockContext);
  const [input, setInput] = useState("");
  const [bestMatches, setBestMatches] = useState([]);

  const updateBestMatches = async () => {
    try {
      if (input) {
        const response = await axios.get(`${API_BASE}/search?query=${input}`);
        const searchResults = response.data;
        setBestMatches(searchResults.result);
      }
    } catch (error) {
      setBestMatches([]);
      console.error(error);
    }
  };

  const clear = () => {
    setInput("");
    setBestMatches([]);
  };

  const handleSelect = (symbol) => {
    setStockSymbol(symbol);
    clear();
  };

  return (
    <div
      className={`flex items-center my-4 border-2 rounded-md relative z-50 w-96 ${
        darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-neutral-200"
      }`}
    >
      <input
        type="text"
        value={input}
        className={`w-full px-4 py-2 focus:outline-none rounded-md ${
          darkMode ? "bg-gray-900" : ""
        }`}
        placeholder="Search stock..."
        onChange={(event) => setInput(event.target.value)}
        onKeyPress={(event) => {
          if (event.key === "Enter") {
            updateBestMatches();
          }
        }}
      />
      {input && (
        <button onClick={clear} className="m-1">
          <XIcon className="h-4 w-4 fill-gray-500" />
        </button>
      )}
      <button
        onClick={updateBestMatches}
        className="h-8 w-8 bg-indigo-600 rounded-md flex justify-center items-center m-1 p-2 transition duration-300 hover:ring-2 ring-indigo-400"
      >
        <SearchIcon className="h-4 w-4 fill-gray-100" />
      </button>
      {input && bestMatches.length > 0 ? (
        <SearchResults results={bestMatches} onSelect={handleSelect} />
      ) : null}
    </div>
  );
};

export default Search;
