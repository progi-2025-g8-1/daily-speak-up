from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import thirdparty, passwordless, session
from supertokens_python.recipe.thirdparty.provider import ProviderInput, ProviderConfig, ProviderClientConfig
from supertokens_python.recipe.passwordless import ContactEmailOnlyConfig, CreateAndSendCustomEmailParameters
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryInterface, EmailDeliveryConfig
from typing import Dict, Any, Optional
from ..api.config import get_settings
from .email_service import EmailService


def custom_email_deliver(original_implementation: EmailDeliveryInterface):
    """Custom email delivery implementation using EmailService"""
    original_send_email = original_implementation.send_email
    
    async def send_email(input_: CreateAndSendCustomEmailParameters, user_context: Dict[str, Any]):
        settings = get_settings()
        
        try:
            code: Optional[str] = input_.user_input_code if hasattr(input_, 'user_input_code') else None
            magic_link: Optional[str] = input_.url_with_link_code if hasattr(input_, 'url_with_link_code') else None
            
            try:
                import os
                with open("latest_otp.txt", "w") as f:
                    f.write(str(code))
                
                if magic_link:
                     with open("latest_link.txt", "w") as f:
                        f.write(str(magic_link))
            except Exception as e:
                print(f"Failed to write OTP to file: {e}")

            EmailService.send_email(
                to_mail=input_.email,
                subject="Your Sign In Code - DailySpeakUp",
                message="",
                template='passwordless_login',
                code=code,
                magic_link=magic_link
            )
            
        except Exception as e:
            await original_send_email(input_, user_context)
    
    original_implementation.send_email = send_email
    return original_implementation


def init_supertokens():
    settings = get_settings()
    
    init(
        app_info=InputAppInfo(
            app_name=settings.app_name,
            api_domain=settings.api_domain,
            website_domain=settings.website_domain,
            api_base_path=settings.api_base_path,
            website_base_path="/auth"
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.supertokens_connection_uri,
            api_key=settings.supertokens_api_key,
        ),
        framework='fastapi',
        recipe_list=[
            thirdparty.init(
                sign_in_and_up_feature=thirdparty.SignInAndUpFeature(
                    providers=[
                        ProviderInput(
                            config=ProviderConfig(
                                third_party_id="google",
                                clients=[
                                    ProviderClientConfig(
                                        client_id=settings.google_client_id,
                                        client_secret=settings.google_client_secret,
                                    ),
                                ],
                            ),
                        ),
                    ]
                )
            ),
            passwordless.init(
                contact_config=ContactEmailOnlyConfig(),
                flow_type="USER_INPUT_CODE_AND_MAGIC_LINK",
                email_delivery=EmailDeliveryConfig(
                    override=custom_email_deliver
                ),
            ),
            session.init(
                cookie_same_site="none" if settings.environment == "production" else "lax",
                cookie_secure=True if settings.environment == "production" else False,
            )
        ]
    )
