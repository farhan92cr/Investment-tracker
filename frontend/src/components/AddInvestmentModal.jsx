import React, { useEffect, useState } from 'react'
import { X, Plus } from 'lucide-react'
import api from '../lib/api'

export default function AddInvestmentModal({ onClose, onSaved }) {
  const [stocks, setStocks] = useState([])
  const [mode, setMode] = useState('existing') // 'existing' | 'new'
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const [ticker, setTicker] = useState('')
  const [newStock, setNewStock] = useState({ ticker: '', company: '', sector: '' })
  const [buy, setBuy] = useState({ bought_price: '', units: '', date_of_buy: '', brok_rate: '' })

  useEffect(() => {
    api.get('/stocks').then((res) => setStocks(res.data))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      let finalTicker = ticker
      if (mode === 'new') {
        await api.post('/stocks', newStock)
        finalTicker = newStock.ticker
      }
      await api.post('/buy-transactions', {
        ticker: finalTicker,
        bought_price: parseFloat(buy.bought_price),
        units: parseFloat(buy.units),
        date_of_buy: buy.date_of_buy,
        brok_rate: buy.brok_rate ? parseFloat(buy.brok_rate) : 0,
      })
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save this investment')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
          <h2 style={{ margin: 0, fontFamily: 'var(--font-display)' }}>Add an investment</h2>
          <button className="ghost" onClick={onClose} style={{ padding: 6 }}><X size={18} /></button>
        </div>

        <div style={{ display: 'flex', gap: 8, marginBottom: 18 }}>
          <button
            type="button"
            className={mode === 'existing' ? '' : 'ghost'}
            onClick={() => setMode('existing')}
          >
            Stock I already track
          </button>
          <button
            type="button"
            className={mode === 'new' ? '' : 'ghost'}
            onClick={() => setMode('new')}
          >
            <Plus size={14} style={{ verticalAlign: 'text-bottom' }} /> New stock
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {mode === 'existing' ? (
            <label style={labelStyle}>
              Ticker
              <select value={ticker} onChange={(e) => setTicker(e.target.value)} required style={{ width: '100%' }}>
                <option value="">Select...</option>
                {stocks.map((s) => <option key={s.id} value={s.ticker}>{s.ticker} - {s.company}</option>)}
              </select>
            </label>
          ) : (
            <div style={{ display: 'grid', gap: 10, marginBottom: 6 }}>
              <label style={labelStyle}>Ticker
                <input value={newStock.ticker} onChange={(e) => setNewStock({ ...newStock, ticker: e.target.value.toUpperCase() })} required />
              </label>
              <label style={labelStyle}>Company
                <input value={newStock.company} onChange={(e) => setNewStock({ ...newStock, company: e.target.value })} required />
              </label>
              <label style={labelStyle}>Sector
                <input value={newStock.sector} onChange={(e) => setNewStock({ ...newStock, sector: e.target.value })} required />
              </label>
            </div>
          )}

          <hr style={{ border: 'none', borderTop: '1px solid var(--line)', margin: '16px 0' }} />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <label style={labelStyle}>Bought price
              <input type="number" step="0.01" value={buy.bought_price} onChange={(e) => setBuy({ ...buy, bought_price: e.target.value })} required />
            </label>
            <label style={labelStyle}>Units
              <input type="number" step="1" value={buy.units} onChange={(e) => setBuy({ ...buy, units: e.target.value })} required />
            </label>
            <label style={labelStyle}>Date of buy
              <input type="date" value={buy.date_of_buy} onChange={(e) => setBuy({ ...buy, date_of_buy: e.target.value })} required />
            </label>
            <label style={labelStyle}>Brokerage rate (optional)
              <input type="number" step="0.0001" value={buy.brok_rate} onChange={(e) => setBuy({ ...buy, brok_rate: e.target.value })} />
            </label>
          </div>

          {error && <div className="error-text" style={{ marginTop: 12 }}>{error}</div>}

          <button type="submit" disabled={saving} style={{ width: '100%', marginTop: 18 }}>
            {saving ? 'Saving...' : 'Save investment'}
          </button>
        </form>
      </div>
    </div>
  )
}

const overlayStyle = {
  position: 'fixed', inset: 0, background: 'rgba(11,61,46,0.5)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
}
const modalStyle = {
  background: 'white', borderRadius: 12, padding: 26, width: 420,
  maxHeight: '90vh', overflowY: 'auto', boxShadow: '0 30px 80px rgba(0,0,0,0.4)',
}
const labelStyle = { display: 'flex', flexDirection: 'column', fontSize: 12, color: 'var(--ink-soft)', gap: 4 }
