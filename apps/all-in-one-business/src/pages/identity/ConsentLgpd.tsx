import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ConsentLgpd: React.FC = () => {
  return <SmartCRUD module="identity" entity="consentlgpd" type="form" title="Consent Lgpd" />;
};

export default ConsentLgpd;
