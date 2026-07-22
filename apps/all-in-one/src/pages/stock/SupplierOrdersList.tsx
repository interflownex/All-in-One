import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const SupplierOrdersList: React.FC = () => {
  return <SmartCRUD module="stock" entity="supplierorders" type="list" title="Supplier Orders" />;
};

export default SupplierOrdersList;
