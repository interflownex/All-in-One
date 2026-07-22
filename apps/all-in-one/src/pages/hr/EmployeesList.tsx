import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const EmployeesList: React.FC = () => {
  return <SmartCRUD module="hr" entity="employees" type="list" title="Employees" />;
};

export default EmployeesList;
