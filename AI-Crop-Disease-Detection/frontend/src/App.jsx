import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import DetectPage from './pages/DetectPage';
import DiseasesPage from './pages/DiseasesPage';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#131e35',
              color: '#f8fafc',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '12px',
              fontFamily: 'Inter, sans-serif',
            },
          }}
        />

        {/* Navigation */}
        <Navbar />

        {/* Page routes */}
        <Routes>
          <Route path="/"         element={<HomePage />} />
          <Route path="/detect"   element={<DetectPage />} />
          <Route path="/diseases" element={<DiseasesPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
