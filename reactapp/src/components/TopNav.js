import React, { useContext } from "react";
import ThemeContext from "../context/ThemeContext";
import ThemeIcon from "./ThemeIcon";
import { Link } from "react-router-dom";

const TopNav = () => {
  const { darkMode } = useContext(ThemeContext);

  const handleLogout = () => {
    localStorage.removeItem("user_id");
  };

  return (
    <nav
      className={`w-full flex justify-between items-center xl:top-5 ${
        darkMode ? "bg-gray-900 text-gray-300" : "bg-neutral-100 text-gray-800"
      }`}
    >
      <Link
        className="text-2xl font-bold font-mono underline flex gap-2 mr-16"
        to="/dashboard"
      >
        <img src="logo.png" className="w-8 h-8" />
        <p>Stockbot</p>
      </Link>

      {/* Navigation Links */}
      <ul className="flex space-x-6">
        <li className="cursor-pointer hover:text-indigo-500">
          <Link to="/dashboard">Home</Link>
        </li>
        <li className="cursor-pointer hover:text-indigo-500">
          <Link to="/chat">Chatbot</Link>
        </li>
        <li className="cursor-pointer hover:text-indigo-500">
          <Link to="/portfolio">Portfolio</Link>
        </li>
        <li className="cursor-pointer hover:text-indigo-500">
          <Link to="/" onClick={handleLogout}>
            Logout
          </Link>
        </li>
      </ul>

      <div>
        <ThemeIcon />
      </div>
    </nav>
  );
};

export default TopNav;
