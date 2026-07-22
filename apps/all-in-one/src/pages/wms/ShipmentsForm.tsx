import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ShipmentsForm: React.FC = () => {
  return <SmartCRUD module="wms" entity="shipments" type="form" title="Shipments" />;
};

export default ShipmentsForm;
