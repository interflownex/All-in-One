import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const WalletsForm: React.FC = () => {
  return <SmartCRUD module="finance" entity="wallets" type="form" title="Wallets" />;
};

export default WalletsForm;
