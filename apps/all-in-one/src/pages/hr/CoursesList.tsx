import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CoursesList: React.FC = () => {
  return <SmartCRUD module="hr" entity="courses" type="list" title="Courses" />;
};

export default CoursesList;
