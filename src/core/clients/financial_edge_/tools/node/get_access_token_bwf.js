// This script is a quick POST request to get the required access token from OATH2
// Reference: https://developer.blackbaud.com/skyapi/docs/authorization/auth-code-flow/tutorial#refresh-access-token
// node get_access_token.js

require('dotenv').config()
const axios = require('axios').default;
const querystring = require('querystring');

const TEMP_CODE_FROM_API_RESPONSE = process.env.CODE_BWF
const APPLICATION_ID = process.env.APPLICATION_ID
const APPLICATION_SECRET = process.env.APPLICATION_SECRET
const REDIRECT_URI = process.env.REDIRECT_URI
console.log(TEMP_CODE_FROM_API_RESPONSE, APPLICATION_SECRET, APPLICATION_ID, REDIRECT_URI)
const config = {
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
};

axios
  .post('https://oauth2.sky.blackbaud.com/token', querystring.stringify({
    grant_type: 'authorization_code',
    redirect_uri: REDIRECT_URI,
    code: TEMP_CODE_FROM_API_RESPONSE,
    client_id: APPLICATION_ID,
    client_secret: APPLICATION_SECRET
  }), config)
  .then(res => {
    console.log(`statusCode: ${res.statusCode}`)
    console.log(res)
  })
  .catch(error => {
    console.error(error)
  })