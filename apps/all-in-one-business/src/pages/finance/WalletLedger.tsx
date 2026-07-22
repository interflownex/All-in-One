import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const WalletLedger: React.FC = () => {
  return <SmartCRUD module="finance" entity="walletledger" type="form" title="Wallet Ledger" />;
};

export default WalletLedger;
