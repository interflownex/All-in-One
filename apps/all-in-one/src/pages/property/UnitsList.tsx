import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const UnitsList: React.FC = () => {
  return <SmartCRUD module="property" entity="units" type="list" title="Units" />;
};

export default UnitsList;
