import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const InventoryForm: React.FC = () => {
  return <SmartCRUD module="wms" entity="inventory" type="form" title="Inventory" />;
};

export default InventoryForm;
