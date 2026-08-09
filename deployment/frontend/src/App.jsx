import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import ApiStatusBanner from "./components/ApiStatusBanner.jsx";
import Home from "./pages/Home.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import Product from "./pages/Product.jsx";
import Analytics from "./pages/Analytics.jsx";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-surface via-[#0c0f16] to-[#080a10]">
      <Navbar />
      <ApiStatusBanner />
      <main className="mx-auto max-w-7xl px-4 pb-16 pt-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/product/:id" element={<Product />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </div>
  );
}
