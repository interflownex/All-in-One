import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const FareRulesForm: React.FC = () => {
  return <SmartCRUD module="mobility" entity="farerules" type="form" title="Fare Rules" />;
};

export default FareRulesForm;
