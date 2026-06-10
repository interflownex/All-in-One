import React from 'react';

/**
 * LedgerTransactionList
 * Interface de listagem de transações seguindo a estética Neo-brutalista do Valley Ecosystem.
 * Reforça visualmente a natureza append-only do Ledger.
 */

const transactions = [
    { id: '1', date: '2026-06-01 10:30', description: 'Venda #1092 - Smartphone', amount: 'R$ 1.200,00', type: 'credit' },
    { id: '2', date: '2026-06-01 11:15', description: 'Taxa Marketplace Valley', amount: '- R$ 24,00', type: 'debit' },
    { id: '3', date: '2026-06-01 12:00', description: 'Compra de 100 Pepitas', amount: '- R$ 10,00', type: 'debit' },
    { id: '4', date: '2026-06-01 14:45', description: 'Venda #1093 - Capa Protetora', amount: 'R$ 45,00', type: 'credit' },
];

const LedgerTransactionList: React.FC = () => {
    return (
        <div className="neo-card" style={{ maxWidth: '600px', backgroundColor: 'var(--valley-surface-neutral)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ margin: 0, fontWeight: 900, color: 'var(--valley-deep-purple)' }}>EXTRATO (APPEND-ONLY)</h3>
                <div style={{ backgroundColor: 'var(--valley-cyan)', padding: '5px 10px', border: '2px solid #000', fontWeight: 800 }}>
                    SALDO: R$ 1.211,00
                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {transactions.map((tx) => (
                    <div
                        key={tx.id}
                        style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '12px',
                            border: '2px solid #000',
                            backgroundColor: tx.type === 'credit' ? 'var(--valley-surface-blue)' : 'var(--valley-surface-purple)',
                            boxShadow: '2px 2px 0px 0px #000'
                        }}
                    >
                        <div>
                            <div style={{ fontSize: '0.75rem', fontWeight: 700, opacity: 0.7 }}>{tx.date}</div>
                            <div style={{ fontWeight: 800 }}>{tx.description}</div>
                        </div>
                        <div style={{
                            fontWeight: 900,
                            color: tx.type === 'credit' ? 'var(--valley-success)' : 'var(--valley-error)',
                            fontSize: '1.1rem'
                        }}>
                            {tx.amount}
                        </div>
                    </div>
                ))}
            </div>

            <div style={{ marginTop: '1.5rem', fontSize: '0.7rem', fontStyle: 'italic', textAlign: 'center' }}>
                * Transações imutáveis protegidas pela governança Valley. Proibido UPDATE/DELETE.
            </div>
        </div>
    );
};

export default LedgerTransactionList;