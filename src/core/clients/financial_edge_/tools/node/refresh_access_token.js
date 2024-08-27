// This script is a quick POST request to get the required access token from OATH2
// Reference: https://developer.blackbaud.com/skyapi/docs/authorization/auth-code-flow/tutorial#refresh-access-token
// node get_access_token.js
const axios = require('axios').default;
const querystring = require('querystring');
require('dotenv').load()

// const TEMP_CODE_FROM_API_RESPONSE = 'a5cb0c08e5da4a41b7bb041aa89ba442'
const APPLICATION_ID = process.env.APPLICATION_ID
const APPLICATION_SECRET = process.env.APPLICATION_SECRET
const REFRESH_TOKEN = process.env.REFRESH_TOKEN
const REDIRECT_URI = process.env.REDIRECT_URI

const config = {
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
};

axios
  .post('https://oauth2.sky.blackbaud.com/token', querystring.stringify({
    grant_type: 'refresh_token',
    refresh_token: REFRESH_TOKEN,
    redirect_uri: REDIRECT_URI,
    client_id: APPLICATION_ID,
    client_secret: APPLICATION_SECRET,
    preserve_refresh_token: true
  }), config)
  .then(res => {
    console.log(`statusCode: ${res.statusCode}`)
    console.log(res)
  })
  .catch(error => {
    console.error(error)
  })
