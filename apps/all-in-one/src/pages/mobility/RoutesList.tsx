import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RoutesList: React.FC = () => {
  return <SmartCRUD module="mobility" entity="routes" type="list" title="Routes" />;
};

export default RoutesList;
