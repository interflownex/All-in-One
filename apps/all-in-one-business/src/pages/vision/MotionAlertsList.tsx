import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const MotionAlertsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="vision" 
      entity="motionalerts" 
      type="list" 
      title="Motion Alerts" 
    />
  );
};

export default MotionAlertsList;
