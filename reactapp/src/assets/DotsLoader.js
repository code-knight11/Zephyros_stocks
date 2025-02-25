import React from "react";

const BouncingDotsLoader = () => {
  const loaderStyle = {
    display: "flex",
    justifyContent: "center",
  };

  const dotStyle = {
    width: "10px",
    height: "10px",
    margin: "3px 3px",
    borderRadius: "50%",
    backgroundColor: "#4F46E5",
    opacity: 1,
    animation: "bouncing-loader 0.6s infinite alternate",
  };

  return (
    <div>
      <style>
        {`
          @keyframes bouncing-loader {
            to {
              opacity: 0.1;
              transform: translateY(-16px);
            }
          }
        `}
      </style>
      <div style={loaderStyle}>
        <div style={dotStyle}></div>
        <div style={{ ...dotStyle, animationDelay: "0.2s" }}></div>
        <div style={{ ...dotStyle, animationDelay: "0.4s" }}></div>
      </div>
    </div>
  );
};

export default BouncingDotsLoader;
