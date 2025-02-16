import React, { useContext } from "react";
import { Link } from "react-router-dom";
import ThemeContext from "../context/ThemeContext";
import ThemeIcon from "../components/ThemeIcon";

const SplashScreen = () => {
  const { darkMode } = useContext(ThemeContext);

  return (
    <div
      className={`relative min-h-screen flex flex-col justify-center items-center p-4 ${
        darkMode ? "bg-gray-900 text-gray-300" : "bg-neutral-100 text-gray-800"
      }`}
    >
      {/* Theme Icon positioned at the top right */}
      <div className="absolute top-4 right-4">
        <ThemeIcon />
      </div>

      <h1 className="text-4xl font-bold mb-8">Welcome to StockBot.</h1>
      <div className="flex space-x-4">
        <Link to="/register">
          <button className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
            Register
          </button>
        </Link>
        <Link to="/login">
          <button className="px-6 py-3 border border-indigo-600 text-indigo-600 rounded-md hover:bg-indigo-600 hover:text-white transition">
            Login
          </button>
        </Link>
      </div>
    </div>
  );
};

export default SplashScreen;
