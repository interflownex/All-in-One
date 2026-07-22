import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RolesList: React.FC = () => {
  return <SmartCRUD module="permissions" entity="roles" type="list" title="Roles" />;
};

export default RolesList;
