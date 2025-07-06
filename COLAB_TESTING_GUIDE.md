# Repo Runner Colab Testing Guide

This guide provides instructions for testing the repo_runner package in Google Colab environment.

## Quick Start

### 1. Open the Notebook
- Upload `repo_runner_colab_test.ipynb` to Google Colab
- Or copy the notebook content into a new Colab notebook

### 2. Run All Cells
Execute each cell in sequence to test the complete functionality:

## Cell-by-Cell Instructions

### Cell 1: Environment Setup
```python
# Install system dependencies
!apt-get update -qq
!apt-get install -y git curl wget

# Install Python dependencies
!pip install --upgrade pip
!pip install click transformers torch accelerate requests psutil colorama rich pyyaml jinja2

# Verify installations
import sys
print(f"Python version: {sys.version}")
print("Dependencies installed successfully!")
```

### Cell 2: Clone and Setup
```python
# Clone the repo_runner repository
!git clone https://github.com/your-username/project-bolt-sb1-onurcrax.git
!cd project-bolt-sb1-onurcrax

# Install the repo_runner package in development mode
!cd project-bolt-sb1-onurcrax && pip install -e .

# Verify installation
!which repo_runner || echo "repo_runner not found in PATH"
!python -c "import repo_runner; print('repo_runner imported successfully')"
```

### Cell 3: Test Repository Creation
```python
# Creates a simple Flask test application
# This cell creates a test repository with:
# - app.py (Flask application)
# - requirements.txt (dependencies)
# - README.md (documentation)
```

### Cell 4: Port Manager Test
```python
# Tests the PortManagerAgent functionality
# - Allocates ports for different services
# - Checks port status
# - Tests port release functionality
```

### Cell 5: Individual Agent Tests
```python
# Tests each agent individually:
# - DetectionAgent: Analyzes repository structure
# - RequirementsAgent: Extracts dependencies
# - SetupAgent: Sets up environment
```

### Cell 6: Orchestrator Test with Timeout
```python
# Tests the main orchestrator with 3-minute timeout
# - Runs the complete workflow
# - Handles timeouts gracefully
# - Provides detailed output
```

### Cell 7: CLI Command Test
```python
# Tests the CLI interface with 5-minute timeout
# - Runs repo_runner CLI command
# - Captures stdout/stderr
# - Handles timeouts and errors
```

### Cell 8: Health Monitoring Test
```python
# Tests health monitoring functionality
# - System health checks
# - Service health monitoring
# - Resource usage tracking
```

### Cell 9: Cleanup and Summary
```python
# Cleans up test files and provides summary
# - Removes test repository
# - Shows test results summary
```

## Expected Results

### Successful Test Indicators:
- ✅ All dependencies installed without errors
- ✅ Repo runner package imports successfully
- ✅ Port manager allocates and releases ports correctly
- ✅ Individual agents process test repository
- ✅ Orchestrator completes within timeout
- ✅ CLI command executes successfully
- ✅ Health monitoring provides system metrics
- ✅ Cleanup completes without errors

### Common Issues and Solutions:

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` for repo_runner
**Solution**: Ensure you're in the correct directory and package is installed:
```python
import sys
sys.path.append('/content/project-bolt-sb1-onurcrax')
```

#### 2. Timeout Issues
**Problem**: Tests hang or timeout
**Solution**: The notebook includes timeout mechanisms. If still hanging:
- Restart runtime
- Reduce timeout values
- Check for infinite loops in agent code

#### 3. Port Conflicts
**Problem**: Port allocation fails
**Solution**: Port manager handles conflicts automatically, but if issues persist:
```python
# Manually check port availability
import socket
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0
```

#### 4. Memory Issues
**Problem**: Out of memory errors
**Solution**: Colab has limited RAM. If issues occur:
- Restart runtime
- Clear variables: `%reset`
- Use smaller test repositories

## Customization

### Testing Different Repositories
Replace the test repository creation with your own:

```python
# Clone a specific repository
!git clone https://github.com/username/repo-name.git
test_repo_path = "/content/repo-name"
```

### Adjusting Timeouts
Modify timeout values based on your needs:

```python
# Shorter timeout for quick tests
timeout_seconds = 120  # 2 minutes

# Longer timeout for complex repositories
timeout_seconds = 600  # 10 minutes
```

### Testing Specific Agents
Focus on specific agents by commenting out others:

```python
# Test only detection agent
detection_agent = DetectionAgent()
repo_info = detection_agent.analyze_repository(test_repo_path)
print(f"Repository analysis: {repo_info}")

# Comment out other agent tests
# requirements_agent = RequirementsAgent()
# setup_agent = SetupAgent()
```

## Troubleshooting

### Runtime Disconnection
If Colab disconnects:
1. Reconnect to runtime
2. Re-run setup cells (1-2)
3. Continue from where you left off

### Package Installation Issues
If pip install fails:
```python
# Force reinstall
!pip install --force-reinstall -e /content/project-bolt-sb1-onurcrax

# Or install from requirements
!pip install -r /content/project-bolt-sb1-onurcrax/requirements.txt
```

### Git Issues
If git operations fail:
```python
# Configure git
!git config --global user.name "Test User"
!git config --global user.email "test@example.com"
```

## Performance Tips

1. **Use GPU Runtime**: Enable GPU in Colab for faster LLM inference
2. **Clear Output**: Clear cell outputs to save memory
3. **Restart Runtime**: Restart if memory usage gets high
4. **Batch Tests**: Run multiple tests in sequence rather than parallel

## Next Steps

After successful testing:
1. Deploy to production environment
2. Set up continuous integration
3. Create automated test suite
4. Document any issues found

## Support

If you encounter issues:
1. Check the error messages carefully
2. Verify all dependencies are installed
3. Ensure you're using the latest version
4. Report issues with detailed error logs 