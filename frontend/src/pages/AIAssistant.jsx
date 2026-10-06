import React, { useState } from 'react'
import api from '../lib/api'

export default function AIAssistant() {
  const [message, setMessage] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()

    if (!message.trim() || loading) return

    setLoading(true)
    setError('')
    setAnswer('')

    try {
      const res = await api.post('/ai/chat', {
        message: message.trim(),
      })

      setAnswer(res.data.answer || 'No answer received.')
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Unable to get a response from the AI assistant.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>AI Assistant</h2>
      <p>Ask questions about your investment portfolio.</p>

      <form onSubmit={handleSubmit}>
        <textarea
          rows="5"
          placeholder="Example: What is my current total portfolio value?"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={loading}
          style={{ width: '100%', maxWidth: 700 }}
        />

        <div style={{ marginTop: 10 }}>
          <button type="submit" disabled={loading || !message.trim()}>
            {loading ? 'Thinking...' : 'Ask AI'}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ marginTop: 20 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {answer && (
        <div style={{ marginTop: 20, maxWidth: 700 }}>
          <h3>AI Response</h3>
          <div style={{ whiteSpace: 'pre-wrap' }}>
            {answer}
          </div>
        </div>
      )}
    </div>
  )
}
