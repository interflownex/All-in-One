import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const BiPermissions: React.FC = () => {
  return <SmartCRUD module="bi" entity="bipermissions" type="list" title="Bi Permissões" />;
};

export default BiPermissions;
