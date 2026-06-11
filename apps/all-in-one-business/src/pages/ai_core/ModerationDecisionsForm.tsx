import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ModerationDecisionsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="ai_core" 
      entity="moderationdecisions" 
      type="form" 
      title="Moderation Decisions" 
    />
  );
};

export default ModerationDecisionsForm;
