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