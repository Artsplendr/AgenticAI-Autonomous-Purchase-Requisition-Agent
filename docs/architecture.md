# Architecture

The demo uses a staged workflow:

1. Interpreter parses requisition text
2. Policy checks compliance
3. Supplier agent generates synthetic supplier quotes by category/quantity
4. Optimizer ranks options
5. Approval agent prepares PO and status
