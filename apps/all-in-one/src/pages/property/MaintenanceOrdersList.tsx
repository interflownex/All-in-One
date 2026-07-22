import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const MaintenanceOrdersList: React.FC = () => {
  return (
    <SmartCRUD
      module="property"
      entity="maintenanceorders"
      type="list"
      title="Maintenance Orders"
    />
  );
};

export default MaintenanceOrdersList;
