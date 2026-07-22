import { useState } from "react";

interface SupportModalProps {
  orderTitle: string;
  onClose: () => void;
  onSubmit: (
    kind: "support" | "dispute",
    subject: string,
    message: string,
    desiredResolution: string,
  ) => Promise<{ message: string }>;
}

export default function SupportModal({ orderTitle, onClose, onSubmit }: SupportModalProps) {
  const [kind, setKind] = useState<"support" | "dispute">("support");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [desiredResolution, setDesiredResolution] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [failed, setFailed] = useState(false);

  const submit = async () => {
    if (!message.trim()) {
      setFailed(true);
      setFeedback("Descreva o que aconteceu.");
      return;
    }
    setSubmitting(true);
    setFailed(false);
    setFeedback("");
    try {
      const result = await onSubmit(kind, subject.trim(), message.trim(), desiredResolution.trim());
      setFeedback(result.message);
    } catch (error) {
      setFailed(true);
      setFeedback(error instanceof Error ? error.message : "Nao foi possivel registrar o caso.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content support-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="support-title"
      >
        <header className="modal-header">
          <h2 id="support-title">Abrir suporte</h2>
          <button className="close-btn" onClick={onClose} aria-label="Fechar">
            &times;
          </button>
        </header>
        <div className="modal-body">
          <strong>{orderTitle}</strong>
          <div className="support-kind">
            <button
              type="button"
              className={kind === "support" ? "selected" : ""}
              onClick={() => setKind("support")}
            >
              Suporte
            </button>
            <button
              type="button"
              className={kind === "dispute" ? "selected" : ""}
              onClick={() => setKind("dispute")}
            >
              Disputa
            </button>
          </div>
          <label className="form-group" htmlFor="support-subject">
            <span>Assunto</span>
            <input
              id="support-subject"
              className="neo-input"
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              placeholder="Ex.: atraso na entrega"
              maxLength={200}
            />
          </label>
          <label className="form-group" htmlFor="support-message">
            <span>Mensagem</span>
            <textarea
              id="support-message"
              className="neo-input"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Explique o que ocorreu"
              maxLength={1000}
            />
          </label>
          <label className="form-group" htmlFor="support-resolution">
            <span>Como quer resolver</span>
            <textarea
              id="support-resolution"
              className="neo-input"
              value={desiredResolution}
              onChange={(event) => setDesiredResolution(event.target.value)}
              placeholder="Ex.: reembolso, reenvio, contato do fornecedor"
              maxLength={500}
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
                {submitting ? "Enviando..." : "Registrar caso"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
