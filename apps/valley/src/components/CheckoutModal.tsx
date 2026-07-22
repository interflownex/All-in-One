import React from "react";

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<{ message: string }>;
  offerTitle: string;
  priceAmount: string | null;
}

const CheckoutModal: React.FC<CheckoutModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  offerTitle,
  priceAmount,
}) => {
  const [submitting, setSubmitting] = React.useState(false);
  const [feedback, setFeedback] = React.useState("");
  const [failed, setFailed] = React.useState(false);

  if (!isOpen) return null;

  const submit = async () => {
    setSubmitting(true);
    setFeedback("");
    setFailed(false);
    try {
      const result = await onConfirm();
      setFeedback(result.message || "Pedido criado.");
    } catch (error) {
      setFailed(true);
      setFeedback(error instanceof Error ? error.message : "Nao foi possivel criar o pedido.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content checkout-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="checkout-title"
      >
        <header className="modal-header">
          <h2 id="checkout-title">Finalizar pedido</h2>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">
            &times;
          </button>
        </header>
        <div className="modal-body">
          <h3>{offerTitle}</h3>
          <div className="price-tag">
            {priceAmount
              ? `Total: R$ ${Number(priceAmount).toFixed(2).replace(".", ",")}`
              : "Valor a combinar"}
          </div>
          <p className="mock-info">Revise os dados antes de confirmar.</p>
          {feedback && (
            <p
              className={failed ? "action-feedback error" : "action-feedback success"}
              role="status"
            >
              {feedback}
            </p>
          )}
          <div className="actions">
            <button className="btn-secondary" onClick={onClose}>
              {feedback && !failed ? "Fechar" : "Cancelar"}
            </button>
            {!feedback || failed ? (
              <button className="btn-primary" disabled={submitting} onClick={submit}>
                {submitting ? "Criando pedido..." : "Confirmar pedido"}
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutModal;
