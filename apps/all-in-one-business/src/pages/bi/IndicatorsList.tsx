import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const IndicatorsList: React.FC = () => {
  return <SmartCRUD module="bi" entity="indicators" type="list" title="Indicators" />;
};

export default IndicatorsList;
