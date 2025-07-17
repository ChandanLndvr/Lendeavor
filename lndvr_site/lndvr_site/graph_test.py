from msal import ConfidentialClientApplication

client_id = "cde376bc-d79f-4281-b32e-d2b8ee5187a0"
tenant_id = "514d7679-cdd7-414b-ac8e-31b1908271b6"
client_secret = "4e88Q~PijLxp8Vr9jkZqHfhj9F0AKtMgEC5PQaW7"

app = ConfidentialClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
    client_credential=client_secret
)

token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
print(token_response)
