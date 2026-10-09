import React from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../lib/auth.jsx'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <div className="sidebar">
        <h1>Investment Tracker</h1>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/stocks">Stock Master</NavLink>
        <NavLink to="/buy">Buy Transactions</NavLink>
        <NavLink to="/sold">Sold Transactions</NavLink>
        <NavLink to="/prices">Prices</NavLink>
        <a href="#" onClick={(e) => { e.preventDefault(); logout() }} style={{ marginTop: 20, opacity: 0.8 }}>
          Log out ({user?.email})
        </a>
      </div>
      <div className="main">
        <Outlet />
      </div>
    </div>
  )
}
