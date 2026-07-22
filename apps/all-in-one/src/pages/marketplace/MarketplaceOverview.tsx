import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const MarketplaceOverview: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="marketplace" type="list" title="Marketplace" />;
};

export default MarketplaceOverview;
