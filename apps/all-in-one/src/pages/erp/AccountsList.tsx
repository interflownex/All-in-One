import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AccountsList: React.FC = () => {
  return <SmartCRUD module="erp" entity="accounts" type="list" title="Accounts" />;
};

export default AccountsList;
