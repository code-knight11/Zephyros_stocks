import { useState } from "react";
import "./App.css";
import StockContext from "./context/StockContext";
import ThemeContext from "./context/ThemeContext";
import { Routes, Route } from "react-router-dom";
import Chatbot from "./pages/ChatBot";
import Register from "./pages/Register";
import Login from "./pages/Login"
import SplashScreen from "./pages/SplashScreen";
import { ToastContainer } from "react-toastify";
import DashboardPage from "./pages/Dashboard";
import Portfolio from "./pages/Portfolio";
import ChartArea from "./pages/ChartArea";

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [stockSymbol, setStockSymbol] = useState("MSFT");

  return (
    <ThemeContext.Provider value={{ darkMode, setDarkMode }}>
      <StockContext.Provider value={{ stockSymbol, setStockSymbol }}>
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
          <Routes>
            <Route path="/" element={<SplashScreen />}/>
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/chat" element={<Chatbot />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/chartarea" element={<ChartArea />} />
          </Routes>
      </StockContext.Provider>
    </ThemeContext.Provider>
  );
}

export default App;
