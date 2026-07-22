import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const StockPermissions: React.FC = () => {
  return (
    <SmartCRUD module="stock" entity="stockpermissions" type="list" title="Stock Permissões" />
  );
};

export default StockPermissions;
