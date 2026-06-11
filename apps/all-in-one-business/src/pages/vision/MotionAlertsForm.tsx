import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const MotionAlertsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="vision" 
      entity="motionalerts" 
      type="form" 
      title="Motion Alerts" 
    />
  );
};

export default MotionAlertsForm;
