import React from 'react'

/**
 * A scrolling exchange-board ticker. Hover pauses it and reveals a tooltip.
 * `items`: [{ ticker, price, change, asOf }]  - change is a plain number (+/-),
 * asOf is an optional human-readable string like "2 min ago" or a timestamp.
 */
export default function PriceTicker({ items, demo = false }) {
  if (!items || items.length === 0) return null

  // duplicate the list so the CSS animation (which slides by -50%) loops seamlessly
  const looped = [...items, ...items]

  return (
    <div className="ticker-bar">
      <div className="ticker-track">
        {looped.map((it, i) => (
          <span className="ticker-item" key={i}>
            <span className="t-ticker">{it.ticker}</span>
            <span>{Number(it.price).toFixed(2)}</span>
            {typeof it.change === 'number' && (
              <span className={it.change >= 0 ? 't-up' : 't-down'}>
                {it.change >= 0 ? '▲' : '▼'} {Math.abs(it.change).toFixed(2)}
              </span>
            )}
            <span className="t-tooltip">
              {demo ? 'Sample data — not a live price' : `As of ${it.asOf || 'just now'}`}
            </span>
          </span>
        ))}
      </div>
    </div>
  )
}
