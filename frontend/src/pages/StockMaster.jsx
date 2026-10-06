import React, { useEffect, useState } from 'react'
import api from '../lib/api'

export default function StockMaster() {
  const [stocks, setStocks] = useState([])
  const [form, setForm] = useState({ ticker: '', company: '', sector: '' })
  const [error, setError] = useState('')

  function load() {
    api.get('/stocks').then((res) => setStocks(Array.isArray(res.data) ? res.data : res.data.value || []))
  }
  useEffect(load, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/stocks', form)
      setForm({ ticker: '', company: '', sector: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add stock')
    }
  }

  async function handleDelete(id) {
  const confirmed = window.confirm('Are you sure you want to delete this? This cannot be undone yet.')
  if (!confirmed) return
  await api.delete(`/stocks/${id}`)   // (keep whatever your actual endpoint is per file)
  load()
}

  return (
    <div>
      <h2>Stock Master</h2>
      <p style={{ color: '#5d6d7e', fontSize: 14 }}>
        Add a stock here the first time you buy it - it then becomes selectable on the Buy, Sold, and Prices pages.
      </p>

      <div className="card">
        <form className="form-row" onSubmit={handleSubmit}>
          <label>Ticker
            <input value={form.ticker} onChange={(e) => setForm({ ...form, ticker: e.target.value.toUpperCase() })} required />
          </label>
          <label>Company
            <input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required />
          </label>
          <label>Sector
            <input value={form.sector} onChange={(e) => setForm({ ...form, sector: e.target.value })} required />
          </label>
          <button type="submit">Add stock</button>
        </form>
        {error && <div className="error-text">{error}</div>}

        <table>
          <thead><tr><th>Ticker</th><th>Company</th><th>Sector</th><th></th></tr></thead>
          <tbody>
            {stocks.map((s) => (
              <tr key={s.id}>
                <td>{s.ticker}</td><td>{s.company}</td><td>{s.sector}</td>
                <td><button onClick={() => handleDelete(s.id)} style={{ background: '#c0392b' }}>Remove</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
