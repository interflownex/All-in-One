import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const MarketplacePermissions: React.FC = () => {
  return (
    <SmartCRUD
      module="marketplace"
      entity="marketplacepermissions"
      type="list"
      title="Marketplace Permissões"
    />
  );
};

export default MarketplacePermissions;
