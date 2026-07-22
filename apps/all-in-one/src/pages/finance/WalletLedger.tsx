import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const WalletLedger: React.FC = () => {
  return (
    <SmartCRUD
      module="finance"
      entity="valleygoldledgerentries"
      type="list"
      title="Livro-razão Valley Gold"
    />
  );
};

export default WalletLedger;
