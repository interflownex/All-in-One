import React from 'react';

interface DeleteConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content neo-brutalism">
        <header>
          <h2>DeleteConfirmModal</h2>
          <button onClick={onClose} className="close-btn">&times;</button>
        </header>
        <div className="modal-body">
          <p>Você tem certeza que deseja realizar esta ação?</p>
        </div>
        <footer>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn-primary" onClick={onConfirm}>Confirmar</button>
        </footer>
      </div>
    </div>
  );
};

export default DeleteConfirmModal;
