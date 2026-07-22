import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const LedgerEntriesList: React.FC = () => {
  return <SmartCRUD module="finance" entity="ledgerentries" type="list" title="Ledger Entries" />;
};

export default LedgerEntriesList;
