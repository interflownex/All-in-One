import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const HealthPermissions: React.FC = () => {
  return (
    <SmartCRUD module="health" entity="healthpermissions" type="list" title="Health Permissões" />
  );
};

export default HealthPermissions;
