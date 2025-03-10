# Welcome to CLAM!
### Calvin, Lawrence, Anver, and Maggie's Search Engine.

## Setup:
1. pip install -r "requirements.txt"
2. Create a .env file within the parent directory. 
2. Set the first line of the.env file as: GEMINI_API=AIzaSyD5lm5HrCvSAmu24Zwcx8rOyk_xYD8vhWA. This is the API key used for the AI summaries of our top results.
3. Create a directory in the parent directory: "rsrc"
4. Create a directory in "rsrc": "DEV-2"
5. Within "DEV-2", add every developer directory corresponding to subdomains with file information within.

File Structure (within zipped parent directory):

    ├── rsrc
        └── DEV-2
            ├── aiclub_ics_uci_edu
                ├── 8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json
                ├── 906c24a2203dd5d6cce210c733c48b336ef58293212218808cf8fb88edcecc3b.json
                └── 9a59f63e6facdc3e5fe5aa105c603b545d4145769a107b4dc388312a85cf76d5.json
            ├── alderis_ics_uci_edu ...

3. Run index.py. This may take a while (~600-900 seconds for a M2 MacBook Air).
4. In the terminal, run python app2.py. 
5. The search engine should appear- queries can be made in the search bar, and summaries can be generated for each site on click.

Note: summaries may take 5-30 seconds to load depending on the user's local machine.