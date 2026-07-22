import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const UsersList: React.FC = () => {
  return <SmartCRUD module="identity" entity="users" type="list" title="Users" />;
};

export default UsersList;
