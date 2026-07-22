import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PriceRulesForm: React.FC = () => {
  return <SmartCRUD module="stock" entity="pricerules" type="form" title="Price Rules" />;
};

export default PriceRulesForm;
