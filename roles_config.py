# roles_config.py

ROLE_PERMISSIONS = {
    "Admin": {
        "can_encrypt": True,
        "can_decrypt": True,
        "can_access_dashboard": True
    },
    "Doctor": {
        "can_encrypt": True,
        "can_decrypt": False,
        "can_access_dashboard": True
    },
    "Researcher": {
        "can_encrypt": False,
        "can_decrypt": True,
        "can_access_dashboard": True
    }
}

def has_permission(role, action):
    return ROLE_PERMISSIONS.get(role, {}).get(action, False)
