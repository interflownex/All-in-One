import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PickingWavesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="pickingwaves" 
      type="form" 
      title="Picking Waves" 
    />
  );
};

export default PickingWavesForm;
