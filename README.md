For safest use, install anaconda to create virtual environments for package management: https://docs.anaconda.com/free/anaconda/install/index.html
... or don't, up to you

With conda: 

```conda create -n cascoding-challenge```

```conda activate cascoding-challenge```

```conda install anaconda::pip```

Once you have pip install into your environment (virtual or not):

Open ```bank-statement-reader/keys.py``` and set the OPEN_AI_KEY variable to your OpenAI key to authorize API calls

```python3.12 -m pip install -r requirements.txt```

```python3.12 start.py```

Open the recommended ip from command line output in your browser
