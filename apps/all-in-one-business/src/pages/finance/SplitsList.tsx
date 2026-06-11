import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const SplitsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="splits" 
      type="list" 
      title="Splits" 
    />
  );
};

export default SplitsList;
