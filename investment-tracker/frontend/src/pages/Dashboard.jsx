import React, { useEffect, useState } from 'react'
import api from '../lib/api'
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line, ResponsiveContainer,
} from 'recharts'

const SECTOR_COLORS = ['#F4B942', '#2E86AB', '#8E44AD', '#C0392B', '#16A085', '#D35400', '#7F8C8D', '#B7950B']

function fmt(n) {
  if (n === null || n === undefined) return '-'
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

export default function Dashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/dashboard').then((res) => setData(res.data))
  }, [])

  if (!data) return <p>Loading...</p>

  const gainLossData = data.by_stock.map((s) => ({
    ticker: s.ticker,
    gain_loss: s.unrealized_gain_loss ?? 0,
  }))

  const growthData = data.growth.map((g) => ({
    date: new Date(g.recorded_at).toLocaleDateString(),
    invested: g.total_invested,
    value: g.total_current_value,
  }))

  return (
    <div>
      <h2>Dashboard</h2>

      <div className="kpi-grid">
        <div className="kpi"><div className="label">Total invested</div><div className="value">{fmt(data.total_invested)}</div></div>
        <div className="kpi"><div className="label">Current value</div><div className="value">{fmt(data.total_current_value)}</div></div>
        <div className="kpi"><div className="label">Gain / loss</div><div className="value">{fmt(data.unrealized_gain_loss)}</div></div>
        <div className="kpi"><div className="label">Holdings</div><div className="value">{data.holdings}</div></div>
        <div className="kpi"><div className="label">Sectors</div><div className="value">{data.sectors}</div></div>
        <div className="kpi"><div className="label">Charges paid</div><div className="value">{fmt(data.total_charges_paid)}</div></div>
      </div>

      <div className="card">
        <h3>Allocation by sector</h3>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie data={data.by_sector} dataKey="total_invested" nameKey="sector" outerRadius={100} label>
              {data.by_sector.map((_, i) => <Cell key={i} fill={SECTOR_COLORS[i % SECTOR_COLORS.length]} />)}
            </Pie>
            <Tooltip formatter={(v) => fmt(v)} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3>Invested vs current value by stock</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data.by_stock}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="ticker" />
            <YAxis />
            <Tooltip formatter={(v) => fmt(v)} />
            <Legend />
            <Bar dataKey="total_invested" name="Invested" fill="#1e8449" />
            <Bar dataKey="current_value" name="Current value" fill="#c9a227" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3>Unrealized gain / loss by stock</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={gainLossData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="ticker" />
            <YAxis />
            <Tooltip formatter={(v) => fmt(v)} />
            <Bar dataKey="gain_loss" name="Gain / loss">
              {gainLossData.map((row, i) => (
                <Cell key={i} fill={row.gain_loss >= 0 ? '#1e8449' : '#c0392b'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3>Portfolio growth over time</h3>
        {growthData.length === 0 ? (
          <p style={{ color: '#5d6d7e' }}>Enter a price on the Prices page to start building this chart.</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={growthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(v) => fmt(v)} />
              <Legend />
              <Line type="monotone" dataKey="invested" name="Invested" stroke="#5d6d7e" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="value" name="Current value" stroke="#1e8449" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
