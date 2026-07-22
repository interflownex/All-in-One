import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PayablesList: React.FC = () => {
  return <SmartCRUD module="erp" entity="payables" type="list" title="Payables" />;
};

export default PayablesList;
