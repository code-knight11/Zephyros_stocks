import React, { useContext } from "react";
import ThemeContext from "../context/ThemeContext";
import { MoonIcon } from "@heroicons/react/solid";

const ThemeIcon = () => {
  const { darkMode, setDarkMode } = useContext(ThemeContext);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <button
      onClick={toggleDarkMode}
      className={`rounded-lg border-1 border-neutral-400 p-2 absolute right-7 xl:right-7 xl:top-7 shadow-lg transition duration-300 hover:scale-125 ${
        darkMode ? "shadow-gray-800" : null
      }`}
    >
      <MoonIcon
        className={`h-5 w-5 cursor-pointer stroke-1 ${
          darkMode
            ? "fill-yellow-400 stroke-yellow-400"
            : "fill-none stroke-neutral-400"
        }`}
      />
    </button>
  );
};

export default ThemeIcon;
