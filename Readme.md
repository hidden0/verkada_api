# Verkada API

## Overview

The Verkada API project provides a framework to interact with Verkada's security camera and alarm systems. This project allows you to manage devices, retrieve information, and interact with the Verkada cloud API using Python.

## Features

- **Camera Management**: Retrieve and manage data for security cameras.
- **Alarm Management**: Retrieve and manage data for alarm systems.
- **Site-Based Organization**: Organize devices by site for easier management.
- **Extensible and Modular**: Easily extend the functionality to include more device types or features.

## Project Structure

```plaintext
verkada_api/
├── examples/               # Example scripts to showcase how to use the API
├── library/                # Core libraries and modules
│   ├── __init__.py         # Init file for the library
│   ├── alarms_vapi.py      # Module to handle alarm devices
│   └── ...                 # Other modules for cameras, utilities, etc.
├── tests/                  # Unit tests for the project
├── .gitignore              # Git ignore file
├── .sourcery.yaml          # Configuration for Sourcery (code analysis tool)
├── .venv/                  # Python virtual environment
├── LICENSE                 # License information
├── main.py                 # Entry point of the application
└── README.md               # Project README file (this file)
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/verkada_api.git
   cd verkada_api
   ```

2. **Set up a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Running the main application:**

   ```bash
   python main.py
   ```

2. **Using example scripts:**
   - Example scripts are provided in the `examples/` directory to demonstrate how to interact with the API.

3. **API Structure:**
   - The core functionality is provided through modules in the `library/` directory, such as `alarms_vapi.py` and `camera_vapi.py`.

## Testing

1. **Running tests:**

   ```bash
   pytest tests/
   ```

## Contributing

If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new feature branch.
3. Make your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, feel free to open an issue or contact me at [your.email@example.com].
