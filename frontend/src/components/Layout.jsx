import React from 'react'
import { NavLink, Outlet, Link } from 'react-router-dom'
import { useAuth } from '../lib/auth.jsx'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <div className="sidebar">
        <Link to="/" style={{ textDecoration: 'none' }}><h1>ShariahMate<span style={{ color: '#c9a227' }}>.</span></h1></Link>
        <NavLink to="/app" end>Dashboard</NavLink>
        <NavLink to="/app/stocks">Stock Master</NavLink>
        <NavLink to="/app/buy">Buy Transactions</NavLink>
        <NavLink to="/app/sold">Sold Transactions</NavLink>
        <NavLink to="/app/prices">Prices</NavLink>
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
