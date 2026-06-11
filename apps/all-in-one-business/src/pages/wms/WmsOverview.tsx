import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const WmsOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="wms" 
      type="list" 
      title="Wms" 
    />
  );
};

export default WmsOverview;
