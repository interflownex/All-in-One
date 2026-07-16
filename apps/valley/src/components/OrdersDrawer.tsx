import React, { useEffect, useState } from 'react'
import SupportModal from './SupportModal'
import ReviewModal from './ReviewModal'
import { getOrders, submitReview as submitReviewAction, submitSupportCase, type OrderItem } from '../lib/valleyPlatform'

interface OrdersDrawerProps {
  isOpen: boolean
  onClose: () => void
  token: string | null
}

const statusMap: Record<string, string> = {
  created: 'Aguardando pagamento',
  awaiting_payment: 'Aguardando pagamento',
  paid: 'Pagamento aprovado',
  accepted: 'Pedido aceito',
  in_progress: 'Em andamento',
  delivered: 'Entregue',
  completed: 'Concluido',
  cancelled: 'Cancelado',
  refunded: 'Reembolsado',
  disputed: 'Em disputa',
}

const OrdersDrawerContent: React.FC<{ onClose: () => void; token: string }> = ({ onClose, token }) => {
  const [items, setItems] = useState<OrderItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reviewOrder, setReviewOrder] = useState<OrderItem | null>(null)
  const [supportOrder, setSupportOrder] = useState<OrderItem | null>(null)
  const [reviewedOrders, setReviewedOrders] = useState<Set<string>>(new Set())

  useEffect(() => {
    getOrders(token)
      .then(data => {
        setItems(data)
      })
      .catch(err => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [token])

  const submitReview = async (rating: number, comment: string) => {
    if (!reviewOrder) throw new Error('Selecione um pedido concluido.')
    const payload = await submitReviewAction(reviewOrder.id, rating, comment, token)
    setReviewedOrders(current => new Set(current).add(reviewOrder.id))
    return payload
  }

  const submitSupport = async (kind: 'support' | 'dispute', subject: string, message: string, desiredResolution: string) => {
    if (!supportOrder) throw new Error('Selecione um pedido para abrir suporte.')
    return submitSupportCase(supportOrder.id, kind, subject, message, desiredResolution, token)
  }

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} role="presentation">
        <div className="drawer-content orders-drawer" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="drawer-title">
        <header className="drawer-header">
          <h2 id="drawer-title">Meus Pedidos e Agendamentos</h2>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">&times;</button>
        </header>
        <div className="drawer-body">
          {loading && <div className="loader"></div>}
          {error && <p className="notice error">{error}</p>}
          {!loading && !error && items.length === 0 && (
            <div className="empty-state">
              <p>Voce ainda nao tem pedidos ou agendamentos.</p>
            </div>
          )}
          {!loading && !error && items.length > 0 && (
            <div className="orders-list">
              {items.map(item => (
                <article key={`${item.kind}-${item.id}`} className="order-card">
                  <div className="order-header">
                    <span className="badge">{item.kind === 'appointment' ? 'Agendamento' : item.kind === 'service' ? 'Servico' : 'Pedido'}</span>
                    <span className="date">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  <div className="order-details">
                    <strong>{item.title}</strong>
                    <p>Status: {statusMap[item.status] || item.status}</p>
                    {item.amount_brl && <p className="price">Valor: R$ {Number(item.amount_brl).toFixed(2).replace('.', ',')}</p>}
                    {item.scheduled_at && <p className="schedule">Agendado para: {new Date(item.scheduled_at).toLocaleString()}</p>}
                    {['paid', 'accepted', 'in_progress', 'delivered', 'completed'].includes(item.status) && (
                      <button
                        className="btn-secondary review-action"
                        onClick={() => setSupportOrder(item)}
                      >
                        Abrir suporte
                      </button>
                    )}
                    {['delivered', 'completed'].includes(item.status) && (
                      <button
                        className="btn-secondary review-action"
                        disabled={reviewedOrders.has(item.id)}
                        onClick={() => setReviewOrder(item)}
                      >
                        {reviewedOrders.has(item.id) ? 'Avaliacao enviada' : 'Avaliar'}
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
      </div>
      {reviewOrder && (
        <ReviewModal
          orderTitle={reviewOrder.title}
          onClose={() => setReviewOrder(null)}
          onSubmit={submitReview}
        />
      )}
      {supportOrder && (
        <SupportModal
          orderTitle={supportOrder.title}
          onClose={() => setSupportOrder(null)}
          onSubmit={submitSupport}
        />
      )}
    </>
  )
}

const OrdersDrawer: React.FC<OrdersDrawerProps> = ({ isOpen, onClose, token }) => {
  if (!isOpen || !token) return null
  return <OrdersDrawerContent onClose={onClose} token={token} />
}

export default OrdersDrawer
