import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const InvoicesList: React.FC = () => {
  return <SmartCRUD module="finance" entity="invoices" type="list" title="Invoices" />;
};

export default InvoicesList;
