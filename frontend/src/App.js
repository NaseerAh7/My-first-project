import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Portfolio from "@/pages/Portfolio";
import Admin from "@/pages/Admin";
import { Toaster } from "@/components/ui/toaster";

function App() {
  return (
    <div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Portfolio />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </div>
  );
}

export default App;
