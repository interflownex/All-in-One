import React, { useState } from 'react';

/**
 * PepitaWidget
 * Implementa a interface de gamificação Valley seguindo a estética Neo-brutalista.
 * Permite a seleção manual de 1, 10 ou 100 Pepitas.
 */

interface PepitaWidgetProps {
    onSelect: (amount: number) => void;
    initialAmount?: number;
}

const PepitaWidget: React.FC<PepitaWidgetProps> = ({ onSelect, initialAmount = 10 }) => {
    const [selected, setSelected] = useState<number>(initialAmount);
    const options = [1, 10, 100];

    const handleSelect = (amount: number) => {
        setSelected(amount);
        onSelect(amount);
    };

    return (
        <div className="neo-card" style={{ maxWidth: '300px' }}>
            <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 900, color: 'var(--valley-deep-purple)' }}>
                    GAMIFICAÇÃO VALLEY
                </h4>
                <p style={{ margin: '0.2rem 0', fontSize: '0.85rem', color: '#666' }}>
                    Selecione a recompensa para esta venda:
                </p>
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between' }}>
                {options.map((option) => {
                    const isSelected = selected === option;
                    return (
                        <button
                            key={option}
                            onClick={() => handleSelect(option)}
                            className="neo-button"
                            style={{
                                flex: 1,
                                padding: '10px 0',
                                cursor: 'pointer',
                                backgroundColor: isSelected ? 'var(--valley-cyan)' : 'var(--valley-lavender)',
                                transform: isSelected ? 'translate(2px, 2px)' : 'none',
                                boxShadow: isSelected ? 'var(--valley-shadow-active)' : 'var(--valley-shadow)',
                                transition: 'all 0.1s ease-in-out',
                            }}
                        >
                            <span style={{ display: 'block', fontSize: '1.1rem' }}>💎</span>
                            <span style={{ fontSize: '1rem' }}>{option}</span>
                        </button>
                    );
                })}
            </div>

            <div
                style={{
                    marginTop: '1.2rem',
                    padding: '8px',
                    backgroundColor: 'var(--valley-surface-purple)',
                    border: '1px dashed var(--valley-violet)',
                    fontSize: '0.8rem',
                    textAlign: 'center',
                    fontWeight: 600
                }}
            >
                RECOMPENSA ATUAL: {selected} PEPITAS
            </div>
        </div>
    );
};

export default PepitaWidget;