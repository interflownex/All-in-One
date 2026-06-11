import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ExportsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="bi" 
      entity="exports" 
      type="list" 
      title="Exports" 
    />
  );
};

export default ExportsList;
