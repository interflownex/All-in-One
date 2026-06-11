import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const LedgerEntriesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="ledgerentries" 
      type="form" 
      title="Ledger Entries" 
    />
  );
};

export default LedgerEntriesForm;
