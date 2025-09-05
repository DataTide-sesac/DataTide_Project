import React from 'react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-placeholder">
          <div className="logo-box">LOGO</div>
          <h1>수산물 유통 예측 시스템</h1>
        </div>
      </div>
    </header>
  );
}

export default Header;