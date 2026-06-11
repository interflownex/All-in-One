import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const FoldersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="document" 
      entity="folders" 
      type="form" 
      title="Folders" 
    />
  );
};

export default FoldersForm;
