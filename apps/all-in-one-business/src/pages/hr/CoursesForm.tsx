import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CoursesForm: React.FC = () => {
  return <SmartCRUD module="hr" entity="courses" type="form" title="Courses" />;
};

export default CoursesForm;
