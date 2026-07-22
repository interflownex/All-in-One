import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const InvoicesForm: React.FC = () => {
  return <SmartCRUD module="finance" entity="invoices" type="form" title="Invoices" />;
};

export default InvoicesForm;
