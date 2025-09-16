# DataTide 프로젝트

## 프로젝트 개요

- 수산물의 생산량과 판매량 예측을 목표로 한 AI 기반 데이터 분석 및 시각화 플랫폼
- React 프론트엔드, FastAPI 백엔드, PyTorch 기반 AI 모델 구성

## 팀 구성

- 데이터 전처리 / 분석: 이형주, 임정훈
- AI 모델링: 안수현
- 웹 프론트엔드: 신지원
- 웹 백엔드: 이나리
- 발표자료 제작: 전체 팀

## 프로젝트 일정

| 구분 | 시작일 | 종료일 | 주요 작업 |
|----|-------|-------|---------|
| 분석 | 8월 20일 | 8월 29일 | 프로젝트 계획서 작성, 데이터 수집 |
| 모델 개발 | 8월 29일 | 9월 12일 | 모델 설계, 학습, 튜닝 |
| 웹 서비스 구현 | 8월 28일 | 9월 9일 | 프론트엔드 UI 개발 및 백엔드 API 연동 |
| 마무리 | 9월 16일 | 9월 22일 | 발표 자료 준비, 최종 발표 |

## 기술 스택

- 언어: Python, React, JavaScript, HTML, CSS, MySQL
- 라이브러리: pandas, numpy, sklearn, pytorch, matplotlib, seaborn, plotly
- 도구: Visual Studio Code, GitHub

## 데이터 구조 (ERD)

![ERD 이미지](./erd.jpg)


# React 코드에서 다음과 같이 사용:(javascript)
- const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'