import React, { useEffect, useState } from 'react'
import api from '../lib/api'

export default function Prices() {
  const [latest, setLatest] = useState([])
  const [stocks, setStocks] = useState([])
  const [form, setForm] = useState({ ticker: '', price: '' })
  const [error, setError] = useState('')

  function load() {
    api.get('/prices/latest').then((res) => setLatest(res.data))
    api.get('/stocks').then((res) => setStocks(res.data))
  }
  useEffect(load, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/prices', { ticker: form.ticker, price: parseFloat(form.price) })
      setForm({ ticker: '', price: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save price')
    }
  }

  return (
    <div>
      <h2>Current prices</h2>
      <p style={{ color: '#5d6d7e', fontSize: 14 }}>
        Enter a price any time - it's saved with the exact date and time, and the dashboard's growth
        chart updates right away. Enter the same stock multiple times a day if you want.
      </p>

      <div className="card">
        <form className="form-row" onSubmit={handleSubmit}>
          <label>Ticker
            <select value={form.ticker} onChange={(e) => setForm({ ...form, ticker: e.target.value })} required>
              <option value="">Select...</option>
              {stocks.map((s) => <option key={s.id} value={s.ticker}>{s.ticker}</option>)}
            </select>
          </label>
          <label>Latest price
            <input type="number" step="0.01" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} required />
          </label>
          <button type="submit">Save price</button>
        </form>
        {error && <div className="error-text">{error}</div>}

        <table>
          <thead><tr><th>Ticker</th><th>Latest price</th><th>Recorded at</th></tr></thead>
          <tbody>
            {latest.map((p) => (
              <tr key={p.id}>
                <td>{p.ticker}</td>
                <td>{p.price.toFixed(2)}</td>
                <td>{new Date(p.recorded_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
