import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const WalletsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="wallets" 
      type="list" 
      title="Wallets" 
    />
  );
};

export default WalletsList;
