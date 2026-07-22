import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ServicesOverview: React.FC = () => {
  return <SmartCRUD module="services" entity="services" type="list" title="Services" />;
};

export default ServicesOverview;
