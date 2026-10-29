import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import IndicatorsPage from "./pages/indicators/IndicatorsPage";
import IndicatorDetailPage from "./pages/indicators/IndicatorDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route 
            index element={<Dashboard />} 
          />
          <Route
            path="indicators"
            element={<IndicatorsPage />}
          />
          <Route
            path="/indicators/:code"
            element={<IndicatorDetailPage />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
