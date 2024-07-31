from . import user_handler, admin_handler, ai_handler

user_router = user_handler.user_router
admin_router = admin_handler.admin_router
get_ai_response = ai_handler.get_ai_response
