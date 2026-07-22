import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PermissionsList: React.FC = () => {
  return <SmartCRUD module="permissions" entity="permissions" type="list" title="Permissões" />;
};

export default PermissionsList;
