import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ConsentRecordsList: React.FC = () => {
  return (
    <SmartCRUD module="identity" entity="consentrecords" type="list" title="Consent Records" />
  );
};

export default ConsentRecordsList;
