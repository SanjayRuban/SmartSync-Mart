import React from "react";

export default function Home(){
  return (
    <div>
      <h1>Retail Agent — Frontend Test UI</h1>
      <p>
        This frontend exercises the backend endpoints you provided:
        <b> /inventory, /loyalty, /sales </b>.
      </p>
      <p>Use the navigation links to run the six tests described in your spec.</p>
      <ol>
        <li>Inventory / overstock</li>
        <li>Loyalty compute (Bronze / Silver / Gold)</li>
        <li>Loyalty apply (post-checkout)</li>
        <li>Full checkout orchestration (Sales agent)</li>
      </ol>
    </div>
  );
}
