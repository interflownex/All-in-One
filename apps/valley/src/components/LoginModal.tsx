import React, { useState } from 'react'
import { signInWithEmail, signInWithGoogle } from '../lib/valleyPlatform'

interface LoginModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (token: string, userId: string) => void
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegistering, setIsRegistering] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const session = await signInWithEmail(email, password, isRegistering)
      onSuccess(session.token, session.userId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro na requisicao.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setLoading(true)
    setError('')
    try {
      const session = await signInWithGoogle(email.trim() || 'google@valley.app')
      onSuccess(session.token, session.userId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nao foi possivel autenticar com Google.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div className="modal-content login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
        <header className="modal-header">
          <h2 id="login-title">{isRegistering ? 'Criar Conta' : 'Acessar Valley'}</h2>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">&times;</button>
        </header>
        <div className="modal-body">
          <button className="btn-google" type="button" disabled={loading} onClick={handleGoogleLogin}>
            {loading ? 'Conectando...' : 'Continuar com Google'}
          </button>
          <div className="login-separator"><span>ou use e-mail</span></div>
          <form onSubmit={handleSubmit} className="login-form">
            <div className="input-group">
              <label htmlFor="email">E-mail</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seunome@email.com"
              />
            </div>
            <div className="input-group">
              <label htmlFor="password">Senha</label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="********"
              />
            </div>

            {error && <p className="action-feedback error">{error}</p>}

            <div className="actions">
              <button className="btn-primary" type="submit" disabled={loading}>
                {loading ? 'Aguarde...' : isRegistering ? 'Cadastrar' : 'Entrar'}
              </button>
            </div>
          </form>

          <div className="switch-mode">
            <button className="btn-link" onClick={() => setIsRegistering(!isRegistering)}>
              {isRegistering ? 'Ja tenho conta, fazer login' : 'Ainda nao tem conta? Cadastre-se'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginModal
