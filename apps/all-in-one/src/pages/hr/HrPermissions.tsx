import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const HrPermissions: React.FC = () => {
  return <SmartCRUD module="hr" entity="hrpermissions" type="list" title="Hr Permissões" />;
};

export default HrPermissions;
