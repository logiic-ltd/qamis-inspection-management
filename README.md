# Qamis Inspection Management

Qamis Inspection Management is a Frappe-based application designed to streamline the school inspection process. It provides features for scheduling inspections, assigning users, managing checklists, and handling multi-level approvals.

## Features

- **Inspection Scheduling**: Plan and schedule inspections with ease.
- **User Assignment**: Assign inspection teams and manage team members.
- **Checklist Management**: Create and manage inspection checklists.
- **Multi-level Approvals**: Implement workflows with multiple approval stages.
- **API Integration**: Seamlessly integrate with external systems for user, checklist, and school data.

## Installation

To install the Qamis Inspection Management app, use the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app qamis_inspection_management
```

## Usage

- **Accessing Inspections**: View and manage inspections via the Frappe Desk or through API endpoints.
- **API Endpoints**: Use the API to interact with inspections and teams. For example, to get approved inspections, use:
  ```
  http://qamis.localhost:8000/api/resource/Inspection?filters=[["status", "=", "Approved by DG"]]&fields=["*"]
  ```
- **Workflow Management**: Utilize the built-in workflow to handle inspection approvals and rejections.

## Contributing

We welcome contributions to enhance the Qamis Inspection Management app. This project uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/qamis_inspection_management
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

## License

This project is licensed under the MIT License.
