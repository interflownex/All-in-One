import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DashboardsList: React.FC = () => {
  return <SmartCRUD module="bi" entity="dashboards" type="list" title="Dashboards" />;
};

export default DashboardsList;
