
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../lib/auth.jsx'

export default function Signup() {
  const { signup } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    try {
      await signup(email, password)
      setSuccess(true)
      setPassword('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Create account</h2>

        {error && <div className="error-text">{error}</div>}

        {success ? (
          <div>
            <p>
              Your account has been created. Please check your email for
              the verification link before logging in.
            </p>
            <div className="muted-link">
              Already verified? <Link to="/login">Log in</Link>
            </div>
          </div>
        ) : (
          <>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <input
              type="password"
              placeholder="Password (min 8 chars)"
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Creating account...' : 'Sign up'}
            </button>

            <div className="muted-link">
              Already have an account? <Link to="/login">Log in</Link>
            </div>
          </>
        )}
      </form>
    </div>
  )
}
