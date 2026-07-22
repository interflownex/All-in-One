import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ProvidersList: React.FC = () => {
  return <SmartCRUD module="services" entity="providers" type="list" title="Providers" />;
};

export default ProvidersList;
