import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const SupplierOrdersForm: React.FC = () => {
  return <SmartCRUD module="stock" entity="supplierorders" type="form" title="Supplier Orders" />;
};

export default SupplierOrdersForm;
