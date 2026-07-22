import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const OccupationalRecordsList: React.FC = () => {
  return (
    <SmartCRUD module="hr" entity="occupationalrecords" type="list" title="Occupational Records" />
  );
};

export default OccupationalRecordsList;
