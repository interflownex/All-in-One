import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const QuotesForm: React.FC = () => {
  return <SmartCRUD module="services" entity="quotes" type="form" title="Quotes" />;
};

export default QuotesForm;
