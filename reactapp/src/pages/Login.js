import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "react-toastify";
import ThemeContext from "../context/ThemeContext";
import ThemeIcon from "../components/ThemeIcon";

const Login = () => {
  const { darkMode } = useContext(ThemeContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [pswd, setPswd] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    const userData = { username, pswd };
    try {
      const response = await axios.post("http://127.0.0.1:5002/api/login", userData);
      console.log(response.data.message);
      toast.success("Login successful!");
      localStorage.setItem("user_id", response.data.user_id);
      navigate("/dashboard");
    } catch (error) {
      console.log("An error occurred", error);
      toast.error("Login failed. Please try again.");
    }
  };

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

      <h1 className="text-4xl font-bold mb-8">Login</h1>

      {/* Login Form */}
      <form
        onSubmit={handleLogin}
        className="w-full max-w-md dark:bg-gray-800 p-8 rounded-lg shadow-lg outline outline-2 outline-indigo-500"
      >
        {/* Username Input */}
        <div className="mb-4">
          <label
            htmlFor="username"
            className="block text-sm font-medium mb-1 text-gray-400 dark:text-gray-100"
          >
            Username
          </label>
          <input
            type="text"
            id="username"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Password Input */}
        <div className="mb-6">
          <label
            htmlFor="pswd"
            className="block text-sm font-medium mb-1 text-gray-400 dark:text-gray-100"
          >
            Password
          </label>
          <input
            type="password"
            id="pswd"
            placeholder="Enter your password"
            value={pswd}
            onChange={(e) => setPswd(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Login Button */}
        <button
          type="submit"
          className="w-full py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
        >
          Login
        </button>
      </form>

      {/* Link to Register */}
      <p className="mt-4">
        Don't have an account?{" "}
        <button
          onClick={() => navigate("/register")}
          className="text-indigo-600 hover:underline"
        >
          Register
        </button>
      </p>
    </div>
  );
};

export default Login;
