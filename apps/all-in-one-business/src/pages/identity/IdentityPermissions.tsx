import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const IdentityPermissions: React.FC = () => {
  return (
    <SmartCRUD
      module="identity"
      entity="identitypermissions"
      type="list"
      title="Identity Permissões"
    />
  );
};

export default IdentityPermissions;
