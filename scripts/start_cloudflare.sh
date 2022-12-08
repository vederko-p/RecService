API_ADRESS='http://localhost'
API_PORT='7739'

echo Starting cloudflare...
cloudflared tunnel --url $API_ADRESS:$API_PORT
