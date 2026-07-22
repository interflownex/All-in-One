import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const OrdersForm: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="orders" type="form" title="Orders" />;
};

export default OrdersForm;
