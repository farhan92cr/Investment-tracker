
import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../lib/api'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const [message, setMessage] = useState('Verifying your email...')
  const [error, setError] = useState(false)

  useEffect(() => {
    const token = searchParams.get('token')
    const email = searchParams.get('email')

    if (!token || !email) {
      setMessage('This verification link is invalid or incomplete.')
      setError(true)
      return
    }

    api.get('/auth/verify-email', {
      params: { token, email },
    })
      .then((res) => setMessage(res.data.message))
      .catch((err) => {
        setMessage(
          err.response?.data?.detail ||
          'Verification failed. The link may have expired.'
        )
        setError(true)
      })
  }, [searchParams])

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Email Verification</h2>
        <p className={error ? 'error-text' : ''}>{message}</p>
        <div className="muted-link">
          <Link to="/login">Go to login</Link>
        </div>
      </div>
    </div>
  )
}
