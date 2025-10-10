# Devday Bangalore workshop
This repo contains all the codes that would ber taught during the workshop of devday bangalore 

#  Setup the required project 

### Step 1: Clone the project into your directory

```
git clone git@github.com:spcCodes/devday_blr.git
```
### Step 2: Enter the project directory

```
cd devday_blr
```

### Step 3: Install uv ( if not installed)

For Mac/Linux users
```
pip install uv 

or 

brew install uv (mac)
```
Using uv (recommended)
The recommended way is to use the package manager uv as it's fast, efficient, and makes the whole process much easier!
If using uv, we can create a virtual environment in the project directory and install the required packages with two commands.

### Step 4: install the packages using the following command

```
uv venv
uv sync
```

### Step 5 : Set up the .env file

Rename or copy the .env.sample file to .env file

 We will fill in the required environment variables in the next steps.

### Step 6 : Set up the OpenAI API key , Tavily Search api key and Weather api key

#### For OPENAI api keys
```
Create an OpenAI account at platform.openai.com and open up API key page
https://platform.openai.com/settings/organization/api-keys

Create an api key and paste in .env file
```
#### For Tavily api keys
```
Create an Tavily account and open up API key page
Link:
https://app.tavily.com/home

Create an api key and paste in .env file
```

#### For Weather.com api keys
```
Create an Weather API account and create an api key
Link:
https://www.weatherapi.com/my/

Create an api key and paste in .env file
```



## 🧰 Setting up uv on Windows

---

## Prerequisites
- Python 3.10 or higher installed
- Command Prompt or PowerShell access
---

## Installation

### Step 1: Navigate to Your Project Folder

Open Command Prompt (`cmd.exe`) or PowerShell and navigate to your project directory

### Step 2: Install uv

Install uv globally using pip:

```cmd
pip install uv
```

You should see output similar to:

```
Successfully installed uv-0.9.1
```

### Step 3: Locate the Installation Path

Find where uv was installed:

```cmd
pip show uv
```

**Example output:**

```
Name: uv
Version: 0.9.1
Location: c:\users\username\appdata\local\packages\pythonsoftwarefoundation.python.3.10_qbz5n2kfra8p0\localcache\local-packages\python310\site-packages
```

**Note:** The `uv.exe` executable will be in the corresponding `Scripts` folder. For the example above:

```
C:\Users\username\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts
```

### Step 4: Verify uv.exe Exists

Check that the executable is present (replace with your actual path):

```cmd
dir "C:\Users\username\AppData\Local\...\Python310\Scripts"
```

You should see `uv.exe` listed in the output.

---

## Configuration

### Step 5: Add uv to Your PATH

If the `uv` command is not recognized, you need to add it to your system PATH:

1. Press `Windows + R`, type `sysdm.cpl`, and hit Enter
2. Navigate to the **Advanced** tab → click **Environment Variables**
3. Under **User variables**, select **Path** → click **Edit**
4. Click **New** and add your Scripts path:
   ```
   C:\Users\username\AppData\Local\...\Python310\Scripts
   ```
5. Click **OK** to save all dialogs
6. **Restart your terminal** for changes to take effect

### Step 6: Verify Installation

Test that uv is accessible:

```cmd
uv --version
```

If successful, you'll see something like:

```
uv 0.9.1
```

🎉 **You're all set!**

---

## Usage

### Sync Project Dependencies

In your project root (where `pyproject.toml` or `requirements.txt` exists), run:

```cmd
uv sync
```

This will install all required dependencies in a virtual environment.

---

## Troubleshooting

### Common Error: Python Version Incompatibility

**Error message:**

```
error: Distribution `onnxruntime==1.23.1` can't be installed because it doesn't have a wheel for CPython 3.14
hint: You're using CPython 3.14 (`cp314`), but `onnxruntime` (v1.23.1) only has wheels for: cp311, cp312, cp313, cp313t
```

**Cause:** Your system Python version is too new, and the package doesn't have compatible binaries yet.

### Solution: Pin to a Compatible Python Version

Use uv to install and pin a compatible Python version (e.g., 3.13):

```cmd
uv python install 3.13
uv python pin 3.13
uv sync
```

**What this does:**

1. Downloads and installs Python 3.13 (if not already available)
2. Pins your project to use Python 3.13
3. Creates a virtual environment with the correct Python version
4. Syncs all dependencies successfully

---

## Quick Reference

### Complete Setup Example

```cmd
# Navigate to your project
cd C:\Users\username\your_project

# Install uv
pip install uv

# Check installation location
pip show uv

# Add to PATH via System Properties (if needed)
# sysdm.cpl → Advanced → Environment Variables → Path → Add Scripts folder

# Verify installation
uv --version

# Sync dependencies
uv sync

# If you encounter Python version issues
uv python install 3.13
uv python pin 3.13
uv sync
```
