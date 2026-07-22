import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CrmPermissions: React.FC = () => {
  return <SmartCRUD module="crm" entity="crmpermissions" type="list" title="Crm Permissões" />;
};

export default CrmPermissions;
