import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const SuppliersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="stock" 
      entity="suppliers" 
      type="form" 
      title="Suppliers" 
    />
  );
};

export default SuppliersForm;
