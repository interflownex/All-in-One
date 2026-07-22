import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const FareRulesList: React.FC = () => {
  return <SmartCRUD module="mobility" entity="farerules" type="list" title="Fare Rules" />;
};

export default FareRulesList;
