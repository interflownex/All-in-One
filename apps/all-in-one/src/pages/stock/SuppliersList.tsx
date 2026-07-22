import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const SuppliersList: React.FC = () => {
  return <SmartCRUD module="stock" entity="suppliers" type="list" title="Suppliers" />;
};

export default SuppliersList;
