# SKY API 

### This module contains all code related to connecting, fetching, posting, and deleting items using the BlackBauds SKYAPI. 

### Resources: 

	1. SKYAPI Getting Started: https://developer.blackbaud.com/skyapi/docs/getting-started

	2. BlackBaud's OAuth authorization code flow for server side applications: 
	https://developer.blackbaud.com/skyapi/docs/authorization/auth-code-flow. 
	This is required to create a semi-permanent authorization token. 

	3. OAUTH NodeJS Tutorial: https://github.com/blackbaud/sky-api-tutorial-auth-code-nodejs/

	4. SkyAPI GL Example: This url is used test connection through blackbauds application. https://developer.sky.blackbaud.com/docs/services/56eb17a0a9db9516c46bff6f/operations/ListJournalEntryBatches

	5. Fantastic use case: https://github.com/tanner-burke/SkyAPI

### Code

#### skyapiclient.py

This file handles the requests made to sky api. Get, Post, Delete, requests are generated here. 

#### baseapi.py 

Prior to executing the API request, the request object or url is generated using this class. 

#### /Entities/
This directory contains all categorical API contructs. For example, journal batch
functions are built within a `journal.py` file to fetch all journal batch data from it's respective url. 


> entities.journal.py --> baseapi.py --> skyapiclient.py



