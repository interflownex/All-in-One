import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const BinsList: React.FC = () => {
  return <SmartCRUD module="wms" entity="bins" type="list" title="Bins" />;
};

export default BinsList;
