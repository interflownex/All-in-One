import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const IdentityVerificationsList: React.FC = () => {
  return (
    <SmartCRUD
      module="identity"
      entity="identityverifications"
      type="list"
      title="Identity Verifications"
    />
  );
};

export default IdentityVerificationsList;
