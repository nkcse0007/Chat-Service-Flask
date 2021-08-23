# Login Types
FORM_LOGIN_TYPE = 'FORM'
PHONE_LOGIN_TYPE = 'PHONE'
GOOGLE_LOGIN_TYPE = 'GOOGLE'
LINKEDIN_LOGIN_TYPE = 'LINKEDIN'
FACEBOOK_LOGIN_TYPE = 'FACEBOOK'
LOGIN_TYPE = (FORM_LOGIN_TYPE, PHONE_LOGIN_TYPE, GOOGLE_LOGIN_TYPE, LINKEDIN_LOGIN_TYPE, FACEBOOK_LOGIN_TYPE)
DEFAULT_LOGIN_TYPE = FORM_LOGIN_TYPE

# =======================================================================================

# Role Type
SUPER_ADMIN_ROLE_TYPE = 'SUPER_ADMIN'
ADMIN_ROLE_TYPE = 'ADMIN'
SHOP_ROLE_TYPE = 'SHOP'
AGENT_ROLE_TYPE = 'AGENT'
AGENCY_ROLE_TYPE = 'AGENCY'
USER_ROLE_TYPE = 'USER'
ROLE_TYPE = (SUPER_ADMIN_ROLE_TYPE, ADMIN_ROLE_TYPE, SHOP_ROLE_TYPE, AGENT_ROLE_TYPE, AGENCY_ROLE_TYPE, USER_ROLE_TYPE)
DEFAULT_ROLE_TYPE = USER_ROLE_TYPE

# =======================================================================================

# Message Types

USER_TEXT_MESSAGE_TYPE = 'USER_TEXT_MESSAGE'
USER_IMAGE_MESSAGE_TYPE = 'USER_IMAGE_MESSAGE'
USER_GIF_MESSAGE_TYPE = 'USER_GIF_MESSAGE'
USER_VIDEO_MESSAGE_TYPE = 'USER_VIDEO_MESSAGE'
USER_AUDIO_MESSAGE_TYPE = 'USER_AUDIO_MESSAGE'
SYSTEM_MESSAGE_TYPE = 'SYSTEM_MESSAGE'
MESSAGE_TYPES = (USER_TEXT_MESSAGE_TYPE, USER_AUDIO_MESSAGE_TYPE, USER_IMAGE_MESSAGE_TYPE, USER_GIF_MESSAGE_TYPE,
                 USER_VIDEO_MESSAGE_TYPE, SYSTEM_MESSAGE_TYPE)
DEFAULT_MESSAGE_TYPE = USER_TEXT_MESSAGE_TYPE

# =======================================================================================

# Payment Status types
PAYMENT_INITIATED = 'PAYMENT_INITIATED'
PAYMENT_PENDING = 'PAYMENT_PENDING'
PAYMENT_SUCCESS = 'PAYMENT_SUCCESS'
PAYMENT_FAILED = 'PAYMENT_FAILED'
PAYMENT_STATUS_TYPES = (PAYMENT_INITIATED, PAYMENT_PENDING, PAYMENT_SUCCESS, PAYMENT_FAILED)
DEFAULT_PAYMENT_STATUS_TYPE = PAYMENT_INITIATED

# =======================================================================================

# Refund Status types
REFUND_GENERATED = 'REFUND_GENERATED'
REFUND_INITIATED = 'REFUND_INITIATED'
REFUND_SUCCESS = 'REFUND_SUCCESS'
REFUND_FAILED = 'REFUND_FAILED'
REFUND_CANCELED = 'REFUND_CANCELED'
REFUND_STATUS_TYPES = (REFUND_GENERATED, REFUND_INITIATED, REFUND_SUCCESS, REFUND_FAILED, REFUND_CANCELED)
DEFAULT_REFUND_STATUS_TYPE = REFUND_GENERATED

# =======================================================================================
