import { useState } from "react";

interface ReviewModalProps {
  orderTitle: string;
  onClose: () => void;
  onSubmit: (rating: number, comment: string) => Promise<{ message: string }>;
}

export default function ReviewModal({ orderTitle, onClose, onSubmit }: ReviewModalProps) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [failed, setFailed] = useState(false);

  const submit = async () => {
    if (!rating) {
      setFailed(true);
      setFeedback("Escolha uma nota de 1 a 5.");
      return;
    }
    setSubmitting(true);
    setFailed(false);
    setFeedback("");
    try {
      const result = await onSubmit(rating, comment.trim());
      setFeedback(result.message);
    } catch (error) {
      setFailed(true);
      setFeedback(
        error instanceof Error ? error.message : "Nao foi possivel publicar a avaliacao.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content review-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="review-title"
      >
        <header className="modal-header">
          <h2 id="review-title">Avaliar experiencia</h2>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">
            &times;
          </button>
        </header>
        <div className="modal-body">
          <strong>{orderTitle}</strong>
          <fieldset className="rating-field">
            <legend>Sua nota</legend>
            <div className="rating-options">
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  type="button"
                  className={rating === value ? "selected" : ""}
                  aria-label={`${value} de 5`}
                  aria-pressed={rating === value}
                  onClick={() => setRating(value)}
                >
                  {value}
                </button>
              ))}
            </div>
          </fieldset>
          <label className="form-group" htmlFor="review-comment">
            <span>Comentario opcional</span>
            <textarea
              id="review-comment"
              className="neo-input"
              value={comment}
              maxLength={1000}
              onChange={(event) => setComment(event.target.value)}
              placeholder="Conte como foi sua experiencia"
            />
          </label>
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
            {(!feedback || failed) && (
              <button className="btn-primary" disabled={submitting} onClick={submit}>
                {submitting ? "Publicando..." : "Publicar avaliacao"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
