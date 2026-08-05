import React from 'react'
import { Link } from 'react-router-dom'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { Wallet, LineChart as LineChartIcon, PieChart as PieIcon, Clock } from 'lucide-react'
import PriceTicker from '../components/PriceTicker.jsx'

const PRODUCT_NAME = 'ShariahMate' // change this to your own brand name - used only here and in the nav

const DEMO_TICKER = [
  { ticker: 'FFC', price: 565.4, change: 2.1 },
  { ticker: 'OGDC', price: 214.8, change: -1.4 },
  { ticker: 'MARI', price: 658.2, change: 5.6 },
  { ticker: 'LUCK', price: 441.0, change: -0.8 },
  { ticker: 'SYS', price: 154.4, change: 1.2 },
]

const DEMO_SECTORS = [
  { name: 'Fertilizer', value: 50231 },
  { name: 'Oil & Gas', value: 103928 },
  { name: 'Tech', value: 20263 },
  { name: 'ETFs', value: 158189 },
]
const SECTOR_COLORS = ['#F4B942', '#2E86AB', '#8E44AD', '#16A085']

const DEMO_STOCKS = [
  { ticker: 'FFC', invested: 50231, value: 52400 },
  { ticker: 'OGDC', invested: 32808, value: 31600 },
  { ticker: 'MARI', invested: 90600, value: 96200 },
  { ticker: 'LUCK', invested: 37936, value: 36900 },
]

export default function Landing() {
  return (
    <div>
      <PriceTicker items={DEMO_TICKER} demo />

      <nav className="landing-nav">
        <div className="brand">{PRODUCT_NAME}<span>.</span></div>
        <div className="nav-links">
          <a href="#how-it-works">How it works</a>
          <a href="#features">Features</a>
          <a href="#preview">Dashboard</a>
        </div>
        <div className="nav-cta">
          <Link to="/login" className="login-link">Log in</Link>
          <Link to="/signup" className="signup-btn">Sign up free</Link>
        </div>
      </nav>

      <section className="hero">
        <div>
          <div className="eyebrow">PSX portfolio tracking</div>
          <h1>Every buy, every sell, every rupee — accounted for.</h1>
          <p className="lede">
            Log your PSX trades and {PRODUCT_NAME} handles the rest: brokerage, SST, levies,
            and a live view of what you actually own. Enter a price any time you check
            the market — your growth chart builds itself from there.
          </p>
          <div className="hero-ctas">
            <Link to="/signup" className="primary">Create your account</Link>
            <a href="#how-it-works" className="secondary">See how it works</a>
          </div>
        </div>

        <div className="sample-card">
          <div className="sample-label">Sample portfolio</div>
          <div className="sample-kpis">
            <div><div className="n mono">389,745</div><div className="l">Invested (PKR)</div></div>
            <div><div className="n mono" style={{ color: '#1e8449' }}>+2,140</div><div className="l">Gain (PKR)</div></div>
          </div>
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={DEMO_STOCKS}>
              <XAxis dataKey="ticker" tick={{ fontSize: 11 }} />
              <YAxis hide />
              <Bar dataKey="invested" fill="#1e8449" radius={[3, 3, 0, 0]} />
              <Bar dataKey="value" fill="#c9a227" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="section" id="how-it-works">
        <h2>How it works</h2>
        <p className="section-sub">Four steps, and you'll never lose track of a trade again.</p>
        <div className="steps">
          <div className="step">
            <div className="step-no mono">01</div>
            <h3>Create your account</h3>
            <p>Free, private, and yours - nobody else sees your holdings.</p>
          </div>
          <div className="step">
            <div className="step-no mono">02</div>
            <h3>Add your stocks</h3>
            <p>Ticker, company, sector - once each, then reuse them for every trade.</p>
          </div>
          <div className="step">
            <div className="step-no mono">03</div>
            <h3>Log buys, sells, prices</h3>
            <p>Enter a price whenever you check it - even a few times a day.</p>
          </div>
          <div className="step">
            <div className="step-no mono">04</div>
            <h3>Watch it add up</h3>
            <p>Charges, gains, and growth over time, calculated for you.</p>
          </div>
        </div>
      </section>

      <section className="section" id="features">
        <h2>Built for how PSX actually works</h2>
        <p className="section-sub">Not a generic spreadsheet template - the math matches how Pakistani brokerages actually charge.</p>
        <div className="feature-grid">
          <div className="feature-card">
            <Wallet className="icon" size={22} />
            <h3>Brokerage, SST & levies handled</h3>
            <p>Every trade's charges are calculated automatically the same way your broker calculates them.</p>
          </div>
          <div className="feature-card">
            <Clock className="icon" size={22} />
            <h3>Prices, any time</h3>
            <p>No "monthly update" - log a price whenever you check the market, timestamped to the minute.</p>
          </div>
          <div className="feature-card">
            <PieIcon className="icon" size={22} />
            <h3>Sector & stock breakdown</h3>
            <p>See exactly where your money sits - by sector, by company, by gain or loss.</p>
          </div>
          <div className="feature-card">
            <LineChartIcon className="icon" size={22} />
            <h3>Growth over time</h3>
            <p>A running curve of what you've put in versus what it's worth now.</p>
          </div>
        </div>
      </section>

      <section className="section preview-section" id="preview">
        <h2>Your dashboard, at a glance</h2>
        <p className="section-sub">A sample view - sign up to see your own numbers here instead.</p>
        <div className="preview-grid">
          <div className="preview-card">
            <h4>ALLOCATION BY SECTOR</h4>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={DEMO_SECTORS} dataKey="value" nameKey="name" outerRadius={80} label>
                  {DEMO_SECTORS.map((_, i) => <Cell key={i} fill={SECTOR_COLORS[i]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="preview-card">
            <h4>INVESTED VS CURRENT VALUE</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={DEMO_STOCKS}>
                <XAxis dataKey="ticker" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="invested" name="Invested" fill="#1e8449" />
                <Bar dataKey="value" name="Current value" fill="#c9a227" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div>{PRODUCT_NAME} - built for tracking your own PSX portfolio.</div>
        <div className="disclaimer">
          {PRODUCT_NAME} is a personal portfolio tracker, not a brokerage or investment advisor.
          Nothing here is financial advice. Prices you enter are your own responsibility to verify.
        </div>
      </footer>
    </div>
  )
}
