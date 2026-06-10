import React, { useState } from 'react';

/**
 * CalculatorWidget
 * Interface de calculadora seguindo a estética Neo-brutalista do Valley Ecosystem.
 */
const CalculatorWidget: React.FC = () => {
    const [display, setDisplay] = useState('0');
    const [equation, setEquation] = useState('');

    const handleNumber = (num: string) => {
        setDisplay(display === '0' ? num : display + num);
    };

    const handleOperator = (op: string) => {
        setEquation(display + ' ' + op + ' ');
        setDisplay('0');
    };

    const calculate = () => {
        try {
            const result = eval(equation + display);
            setDisplay(String(result));
            setEquation('');
        } catch {
            setDisplay('Erro');
        }
    };

    const clear = () => {
        setDisplay('0');
        setEquation('');
    };

    const CalcButton = ({ label, onClick, color = 'var(--valley-surface-neutral)', wide = false }: any) => (
        <button
            onClick={onClick}
            className="neo-button"
            style={{
                flex: wide ? '2' : '1',
                padding: '15px',
                fontSize: '1.2rem',
                backgroundColor: color,
                cursor: 'pointer',
                minWidth: wide ? '120px' : '60px',
                transition: 'all 0.05s active',
            }}
            onMouseDown={(e) => {
                e.currentTarget.style.transform = 'translate(2px, 2px)';
                e.currentTarget.style.boxShadow = 'var(--valley-shadow-active)';
            }}
            onMouseUp={(e) => {
                e.currentTarget.style.transform = 'none';
                e.currentTarget.style.boxShadow = 'var(--valley-shadow)';
            }}
        >
            {label}
        </button>
    );

    return (
        <div className="neo-card" style={{ maxWidth: '320px', backgroundColor: 'var(--valley-surface-purple)' }}>
            <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 900, color: 'var(--valley-deep-purple)' }}>
                    CALCULADORA DE VENDAS
                </h4>
            </div>

            {/* Display */}
            <div className="neo-card" style={{
                backgroundColor: '#000',
                color: 'var(--valley-cyan)',
                textAlign: 'right',
                fontSize: '2rem',
                marginBottom: '15px',
                padding: '10px',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
            }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--valley-lavender)', height: '1rem' }}>{equation}</div>
                {display}
            </div>

            {/* Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
                <CalcButton label="C" onClick={clear} color="var(--valley-error)" />
                <CalcButton label="/" onClick={() => handleOperator('/')} color="var(--valley-cyan)" />
                <CalcButton label="*" onClick={() => handleOperator('*')} color="var(--valley-cyan)" />
                <CalcButton label="-" onClick={() => handleOperator('-')} color="var(--valley-cyan)" />

                <CalcButton label="7" onClick={() => handleNumber('7')} />
                <CalcButton label="8" onClick={() => handleNumber('8')} />
                <CalcButton label="9" onClick={() => handleNumber('9')} />
                <CalcButton label="+" onClick={() => handleOperator('+')} color="var(--valley-cyan)" />

                <CalcButton label="4" onClick={() => handleNumber('4')} />
                <CalcButton label="5" onClick={() => handleNumber('5')} />
                <CalcButton label="6" onClick={() => handleNumber('6')} />
                <CalcButton label="=" onClick={calculate} color="var(--valley-success)" />

                <CalcButton label="1" onClick={() => handleNumber('1')} />
                <CalcButton label="2" onClick={() => handleNumber('2')} />
                <CalcButton label="3" onClick={() => handleNumber('3')} />
                <CalcButton label="0" onClick={() => handleNumber('0')} wide />
            </div>

            <div style={{ marginTop: '15px', fontSize: '0.7rem', fontWeight: 'bold', textAlign: 'center' }}>
                VALLEY BUSINESS - MÓDULO ERP
            </div>
        </div>
    );
};

export default CalculatorWidget;