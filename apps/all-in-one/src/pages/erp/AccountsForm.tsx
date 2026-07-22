import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AccountsForm: React.FC = () => {
  return <SmartCRUD module="erp" entity="accounts" type="form" title="Accounts" />;
};

export default AccountsForm;
