import React from "react";

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (scheduledAt: string, note?: string) => Promise<{ message: string }>;
  offerTitle: string;
}

const BookingModal: React.FC<BookingModalProps> = ({ isOpen, onClose, onConfirm, offerTitle }) => {
  const [date, setDate] = React.useState("");
  const [time, setTime] = React.useState("");
  const [note, setNote] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [feedback, setFeedback] = React.useState("");
  const [failed, setFailed] = React.useState(false);

  if (!isOpen) return null;

  const submit = async () => {
    if (!date || !time) {
      setFailed(true);
      setFeedback("Informe a data e o horario desejados.");
      return;
    }
    setSubmitting(true);
    setFeedback("");
    setFailed(false);
    try {
      const scheduledAt = new Date(`${date}T${time}`).toISOString();
      const result = await onConfirm(scheduledAt, note);
      setFeedback(result?.message || "Solicitacao confirmada.");
    } catch (error) {
      setFailed(true);
      setFeedback(
        error instanceof Error ? error.message : "Nao foi possivel enviar a solicitacao.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content booking-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="booking-title"
      >
        <header className="modal-header">
          <h2 id="booking-title">Solicitar horario</h2>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">
            &times;
          </button>
        </header>
        <div className="modal-body">
          <h3>{offerTitle}</h3>
          <p className="mock-info">Escolha uma data e um horario de preferencia.</p>
          <div className="form-group">
            <label htmlFor="booking-date">Data desejada</label>
            <input
              id="booking-date"
              type="date"
              className="neo-input"
              value={date}
              onChange={(event) => setDate(event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="booking-time">Horario aproximado</label>
            <input
              id="booking-time"
              type="time"
              className="neo-input"
              value={time}
              onChange={(event) => setTime(event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="booking-note">Detalhes do pedido</label>
            <textarea
              id="booking-note"
              className="neo-input"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              maxLength={500}
            />
          </div>
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
              {feedback && !failed ? "Fechar" : "Voltar"}
            </button>
            {!feedback || failed ? (
              <button className="btn-primary" disabled={submitting} onClick={submit}>
                {submitting ? "Enviando..." : "Enviar solicitacao"}
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingModal;
