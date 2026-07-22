import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const VehiclesList: React.FC = () => {
  return <SmartCRUD module="riders" entity="vehicles" type="list" title="Vehicles" />;
};

export default VehiclesList;
