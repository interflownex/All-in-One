import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const IndicatorsForm: React.FC = () => {
  return <SmartCRUD module="bi" entity="indicators" type="form" title="Indicators" />;
};

export default IndicatorsForm;
