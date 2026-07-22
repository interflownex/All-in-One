import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const KycVerification: React.FC = () => {
  return (
    <SmartCRUD module="identity" entity="kycverification" type="form" title="Kyc Verification" />
  );
};

export default KycVerification;
