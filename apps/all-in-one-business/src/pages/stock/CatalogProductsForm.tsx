import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CatalogProductsForm: React.FC = () => {
  return <SmartCRUD module="stock" entity="catalogproducts" type="form" title="Catalog Products" />;
};

export default CatalogProductsForm;
