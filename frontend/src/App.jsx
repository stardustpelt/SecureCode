// src/App.jsx
import React, { useState } from 'react';
import LandingPage from './pages/LandingPage';
import Analyzer from './pages/Analyzer';
import Documentation from './pages/Documentation';
import About from './pages/About';
import './index.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  if (currentPage === 'home')  return <LandingPage onNavigate={setCurrentPage} />;
  if (currentPage === 'app')   return <Analyzer onNavigate={setCurrentPage} />;
  if (currentPage === 'docs')  return <Documentation onNavigate={setCurrentPage} />;
  if (currentPage === 'about') return <About onNavigate={setCurrentPage} />;

  // Fallback
  return <LandingPage onNavigate={setCurrentPage} />;
}