import React, { useState, useEffect } from "react";
import { Button } from "antd";
// import style from "./style.module.scss";
import workspaceService from "services/workspace.js";

export default function Connection() {
  const [workspaces, setWorkspaces] = useState([]);

  useEffect(() => {
    if (!workspaces.length) {
        fetchWorkspaces();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchWorkspaces = async () => {
    const response = await workspaceService.getWorkspaces();
    setWorkspaces(response.data)
  }

  return (
    <div>
        <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
            <Button
                key="createTag"
                type="primary"
                onClick={(e) => {e.preventDefault();
                    window.location.href='/workspace/add';}
                }
            >
                New Workspace
            </Button>
        </div>
    </div>
    );
  }
