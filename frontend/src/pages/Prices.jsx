import React, { useEffect, useState } from 'react'
import api from '../lib/api'

export default function Prices() {
  const [latest, setLatest] = useState([])
  const [stocks, setStocks] = useState([])
  const [form, setForm] = useState({ ticker: '', price: '' })
  const [error, setError] = useState('')
  const [marketResults, setMarketResults] = useState([])
  const [marketMessage, setMarketMessage] = useState('')
  const [updatingMarket, setUpdatingMarket] = useState(false)

  function load() {
  api.get('/prices/latest').then((res) => {
    setLatest(
      Array.isArray(res.data)
        ? res.data
        : res.data.value || []
    )
  })

  api.get('/stocks').then((res) => {
    setStocks(
      Array.isArray(res.data)
        ? res.data
        : res.data.value || []
    )
  })

  }

  useEffect(load, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    try {
      await api.post('/prices', {
        ticker: form.ticker,
        price: parseFloat(form.price)
      })

      setForm({ ticker: '', price: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save price')
    }
  }

  async function handleMarketUpdate() {
    setError('')
    setMarketMessage('')
    setMarketResults([])
    setUpdatingMarket(true)

    try {
      const res = await api.post('/prices/update-market')

      setMarketMessage(res.data.message)
      setMarketResults(
        Array.isArray(res.data?.results)
          ? res.data.results
          :   []
      )

      load()
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Could not update market prices'
      )
    } finally {
      setUpdatingMarket(false)
    }
  }

  return (
    <div>
      <h2>Current prices</h2>

      <p style={{ color: '#5d6d7e', fontSize: 14 }}>
        Enter a price any time - it's saved with the exact date and time,
        and the dashboard's growth chart updates right away. Enter the same
        stock multiple times a day if you want.
      </p>

      <div className="card">

        <div style={{ marginBottom: 20 }}>
          <h3>Market prices</h3>

          <button
            type="button"
            onClick={handleMarketUpdate}
            disabled={updatingMarket}
          >
            {updatingMarket ? 'Updating...' : 'Update Market Prices'}
          </button>

          {marketMessage && (
            <p style={{ color: '#2e7d32', fontSize: 14 }}>
              {marketMessage}
            </p>
          )}

          {marketResults.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Status</th>
                  <th>Price</th>
                  <th>Source / Reason</th>
                </tr>
              </thead>

              <tbody>
                {marketResults.map((result) => (
                  <tr key={result.ticker}>
                    <td>{result.ticker}</td>

                    <td>
                      {result.status === 'updated'
                        ? ' Updated'
                        : ' Failed'}
                    </td>

                    <td>
                      {result.price !== undefined
                        ? result.price.toFixed(2)
                        : '-'}
                    </td>

                    <td>
                      {result.source || result.reason || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <hr />

        <h3>Manual price entry</h3>

        <form className="form-row" onSubmit={handleSubmit}>
          <label>
            Ticker
            <select
              value={form.ticker}
              onChange={(e) =>
                setForm({ ...form, ticker: e.target.value })
              }
              required
            >
              <option value="">Select...</option>

              {stocks.map((s) => (
                <option key={s.id} value={s.ticker}>
                  {s.ticker}
                </option>
              ))}
            </select>
          </label>

          <label>
            Latest price
            <input
              type="number"
              step="0.01"
              value={form.price}
              onChange={(e) =>
                setForm({ ...form, price: e.target.value })
              }
              required
            />
          </label>

          <button type="submit">
            Save price
          </button>
        </form>

        {error && (
          <div className="error-text">
            {error}
          </div>
        )}

        <h3>Latest recorded prices</h3>

        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Latest price</th>
              <th>Recorded at</th>
            </tr>
          </thead>

          <tbody>
            {latest.map((p) => (
              <tr key={p.id}>
                <td>{p.ticker}</td>
                <td>{p.price.toFixed(2)}</td>
                <td>
                  {new Date(p.recorded_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

      </div>
    </div>
  )
}