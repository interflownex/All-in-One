import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const StreamsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="vision" 
      entity="streams" 
      type="list" 
      title="Streams" 
    />
  );
};

export default StreamsList;
