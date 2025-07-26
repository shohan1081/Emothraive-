from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
import requests

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Your custom logic here
        return user

class DebuggingGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def get_profile_info(self, token):
        """
        This method is overridden for debugging purposes.
        It prints the access token and the response from Google.
        """
        print("--- [DEBUG] Attempting to fetch profile info from Google ---")
        print(f"--- [DEBUG] Using Access Token: {token.token} ---")
        
        headers = {'Authorization': f'Bearer {token.token}'}
        
        try:
            resp = requests.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            profile_data = resp.json()
            print(f"--- [DEBUG] Google API Response (Success): {profile_data} ---")
            return profile_data
        except requests.exceptions.RequestException as e:
            print("--- [DEBUG] Google API Request Failed ---")
            if e.response is not None:
                print(f"--- [DEBUG] Status Code: {e.response.status_code} ---")
                print(f"--- [DEBUG] Response Body: {e.response.text} ---")
            else:
                print(f"--- [DEBUG] Error: {e} ---")
            # Re-raise the exception to allow allauth to handle it as it normally would
            raise