import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "react-toastify";
import ThemeContext from "../context/ThemeContext";
import ThemeIcon from "../components/ThemeIcon";

const Register = () => {
  const { darkMode } = useContext(ThemeContext);
  const navigate = useNavigate();

  // Form state
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [pswd, setPswd] = useState("");
  const [age, setAge] = useState("");

  // Handle form submission
  const handleRegister = async (e) => {
    e.preventDefault();
    const userData = { name, username, email, pswd, age };
    try {
      const response = await axios.post(
        "http://127.0.0.1:5002/api/register",
        userData
      );
      console.log(response.data.message);
      toast.success("Registration successful!");
      navigate("/login");
    } catch (error) {
      console.log("An error occurred", error);
      toast.error("Registration failed!");
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

      <h1 className="text-4xl font-bold mb-8">Registration</h1>

      {/* Registration Form */}
      <form
        onSubmit={handleRegister}
        className="w-full max-w-md dark:bg-gray-800 p-8 rounded-lg shadow-lg outline outline-2 outline-indigo-500"
      >
        {/* Name Input */}
        <div className="mb-4">
          <label
            htmlFor="name"
            className="block text-sm font-medium mb-1 text-gray-400"
          >
            Name
          </label>
          <input
            type="text"
            id="name"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-transparent"
          />
        </div>
        {/* Username Input */}
        <div className="mb-4">
          <label
            htmlFor="username"
            className="block text-sm font-medium mb-1 text-gray-400"
          >
            Username
          </label>
          <input
            type="text"
            id="username"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-transparent"
          />
        </div>
        {/* Email Input */}
        <div className="mb-4">
          <label
            htmlFor="email"
            className="block text-sm font-medium mb-1 text-gray-400"
          >
            Email
          </label>
          <input
            type="email"
            id="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-transparent"
          />
        </div>
        {/* Password Input */}
        <div className="mb-4">
          <label
            htmlFor="pswd"
            className="block text-sm font-medium mb-1 text-gray-400"
          >
            Password
          </label>
          <input
            type="password"
            id="pswd"
            placeholder="Enter your password"
            value={pswd}
            onChange={(e) => setPswd(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-transparent"
          />
        </div>
        {/* Age Input */}
        <div className="mb-6">
          <label
            htmlFor="age"
            className="block text-sm font-medium mb-1 text-gray-400"
          >
            Age
          </label>
          <input
            type="number"
            id="age"
            placeholder="Enter your age"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-transparent"
          />
        </div>
        {/* Register Button */}
        <button
          type="submit"
          className="w-full py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
        >
          Register
        </button>
      </form>

      {/* Link to Login */}
      <p className="mt-4">
        Already have an account?{" "}
        <button
          onClick={() => navigate("/login")}
          className="text-indigo-600 hover:underline"
        >
          Login
        </button>
      </p>
    </div>
  );
};

export default Register;
