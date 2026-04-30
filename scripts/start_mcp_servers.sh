#!/usr/bin/env bash
set -euo pipefail

python -m mcp_servers.erp.server &
python -m mcp_servers.supplier.server &
python -m mcp_servers.policy.server &
python -m mcp_servers.budget.server &
python -m mcp_servers.approval.server &

wait
