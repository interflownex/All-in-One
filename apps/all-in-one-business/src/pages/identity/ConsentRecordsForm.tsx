import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ConsentRecordsForm: React.FC = () => {
  return (
    <SmartCRUD module="identity" entity="consentrecords" type="form" title="Consent Records" />
  );
};

export default ConsentRecordsForm;
