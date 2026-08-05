import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './lib/auth.jsx'
import Layout from './components/Layout.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Dashboard from './pages/Dashboard.jsx'
import StockMaster from './pages/StockMaster.jsx'
import BuyTransactions from './pages/BuyTransactions.jsx'
import SoldTransactions from './pages/SoldTransactions.jsx'
import Prices from './pages/Prices.jsx'

function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <p style={{ padding: 40 }}>Loading...</p>
  if (!user) return <Navigate to="/login" replace />
  return children
}

function HomeRoute() {
  const { user, loading } = useAuth()
  if (loading) return <p style={{ padding: 40 }}>Loading...</p>
  if (user) return <Navigate to="/app" replace />
  return <Landing />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRoute />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/app"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="stocks" element={<StockMaster />} />
        <Route path="buy" element={<BuyTransactions />} />
        <Route path="sold" element={<SoldTransactions />} />
        <Route path="prices" element={<Prices />} />
      </Route>
    </Routes>
  )
}
