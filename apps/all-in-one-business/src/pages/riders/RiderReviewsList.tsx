import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RiderReviewsList: React.FC = () => {
  return <SmartCRUD module="riders" entity="riderreviews" type="list" title="Rider Reviews" />;
};

export default RiderReviewsList;
