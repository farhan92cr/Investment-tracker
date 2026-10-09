import React, { useEffect, useState } from 'react'
import api from '../lib/api'

export default function BuyTransactions() {
  const [rows, setRows] = useState([])
  const [stocks, setStocks] = useState([])
  const [form, setForm] = useState({ ticker: '', bought_price: '', units: '', date_of_buy: '', brok_rate: '' })
  const [error, setError] = useState('')

  function load() {
    api.get('/buy-transactions').then((res) => setRows(Array.isArray(res.data) ? res.data : res.data.value || []))
    api.get('/stocks').then((res) => setStocks(Array.isArray(res.data) ? res.data : res.data.value || []))
  }
  useEffect(load, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/buy-transactions', {
        ...form,
        bought_price: parseFloat(form.bought_price),
        units: parseFloat(form.units),
        brok_rate: form.brok_rate ? parseFloat(form.brok_rate) : 0,
      })
      setForm({ ticker: '', bought_price: '', units: '', date_of_buy: '', brok_rate: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add transaction')
    }
  }


  async function handleDelete(id) {
  if (!window.confirm('Are you sure you want to delete this buy? This cannot be undone yet.')) return
  try {
    await api.delete(`/buy-transactions/${id}`)
    load()
  } catch (err) {
    alert(err.response?.data?.detail || 'Delete failed: ' + err.message)
  }
}

  return (
    <div>
      <h2>Buy transactions</h2>
      <div className="card">
        <form className="form-row" onSubmit={handleSubmit}>
          <label>Ticker
            <select value={form.ticker} onChange={(e) => setForm({ ...form, ticker: e.target.value })} required>
              <option value="">Select...</option>
              {stocks.map((s) => <option key={s.id} value={s.ticker}>{s.ticker}</option>)}
            </select>
          </label>
          <label>Bought price
            <input type="number" step="0.01" value={form.bought_price} onChange={(e) => setForm({ ...form, bought_price: e.target.value })} required />
          </label>
          <label>Units
            <input type="number" step="1" value={form.units} onChange={(e) => setForm({ ...form, units: e.target.value })} required />
          </label>
          <label>Date of buy
            <input type="date" value={form.date_of_buy} onChange={(e) => setForm({ ...form, date_of_buy: e.target.value })} required />
          </label>
          <label>Brokerage rate (optional)
            <input type="number" step="0.0001" value={form.brok_rate} onChange={(e) => setForm({ ...form, brok_rate: e.target.value })} />
          </label>
          <button type="submit">Add buy</button>
        </form>
        {error && <div className="error-text">{error}</div>}

        <table>
          <thead>
            <tr>
              <th>Ticker</th><th>Date</th><th>Price</th><th>Units</th>
              <th>Net paid</th><th>Charges</th><th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.ticker}</td><td>{r.date_of_buy}</td><td>{r.bought_price.toFixed(2)}</td>
                <td>{r.units}</td><td>{r.net_amount_paid.toFixed(2)}</td><td>{r.total_charges.toFixed(2)}</td>
                <td><button onClick={() => handleDelete(r.id)} style={{ background: '#c0392b' }}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
