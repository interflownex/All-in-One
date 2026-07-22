import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CartsForm: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="carts" type="form" title="Carts" />;
};

export default CartsForm;
