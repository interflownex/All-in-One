import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DashboardsForm: React.FC = () => {
  return <SmartCRUD module="bi" entity="dashboards" type="form" title="Dashboards" />;
};

export default DashboardsForm;
