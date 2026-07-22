import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const QuotesList: React.FC = () => {
  return <SmartCRUD module="services" entity="quotes" type="list" title="Quotes" />;
};

export default QuotesList;
