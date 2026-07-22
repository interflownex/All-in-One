import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ProductsForm: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="products" type="form" title="Products" />;
};

export default ProductsForm;
