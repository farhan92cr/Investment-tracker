import React, { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../lib/api'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setMessage('')
    setError(false)
    setLoading(true)

    try {
      const response = await api.post('/auth/reset-password', {
        email: searchParams.get('email'),
        token: searchParams.get('token'),
        new_password: password,
      })
      setMessage(response.data.message)
      setPassword('')
    } catch (err) {
      setError(true)
      setMessage(
        err.response?.data?.detail ||
        'Password reset failed. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const hasResetLink =
    searchParams.get('email') && searchParams.get('token')

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Reset Password</h2>

        {message && (
          <p className={error ? 'error-text' : ''}>{message}</p>
        )}

        {!hasResetLink ? (
          <p>This password-reset link is invalid or incomplete.</p>
        ) : (
          <>
            <input
              type="password"
              placeholder="New password (min 8 chars)"
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset password'}
            </button>
          </>
        )}

        <div className="muted-link">
          <Link to="/login">Go to login</Link>
        </div>
      </form>
    </div>
  )
}