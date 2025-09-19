import React from 'react';
import './Header.css';
import logoImage from '../assets/DataTide_LOGO.png';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-placeholder">
          <div className="logo-box">
            <img src={logoImage} alt="DataTide Logo" className="header-logo" />
          </div>
          <div className="title-group">
            {/* <h1>AI 수산물 수급예측</h1> */}
            <h1>AI로 예측하는 수산물 동향</h1>
            <h5> 수산물 통계와 기상 데이터 기반으로 수산물 생산·판매량을 예측합니다.</h5>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;