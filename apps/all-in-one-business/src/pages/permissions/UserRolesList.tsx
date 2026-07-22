import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const UserRolesList: React.FC = () => {
  return <SmartCRUD module="permissions" entity="userroles" type="list" title="User Roles" />;
};

export default UserRolesList;
