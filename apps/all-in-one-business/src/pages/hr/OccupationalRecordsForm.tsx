import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const OccupationalRecordsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="hr" 
      entity="occupationalrecords" 
      type="form" 
      title="Occupational Records" 
    />
  );
};

export default OccupationalRecordsForm;
