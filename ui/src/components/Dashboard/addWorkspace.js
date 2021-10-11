import React from "react";
import { Steps, Popover } from 'antd';

export default function AddWorkspace() {
    const customDot = (dot, { status, index }) => (
        <Popover
            content={
            <span>
                step {index} status: {status}
            </span>
            }
        >
            {dot}
        </Popover>
    );
  return (
    <>
      <Steps current={1} progressDot={customDot}>
        <Step title="Finished" description="You can hover on the dot." />
        <Step title="In Progress" description="You can hover on the dot." />
        <Step title="Waiting" description="You can hover on the dot." />
        <Step title="Waiting" description="You can hover on the dot." />
      </Steps>
    </>
  );
}
